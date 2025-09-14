"""
FBS FastAPI Management Command for Solution Installation

PRESERVES the sophisticated Django management command functionality.
Converts to FastAPI async patterns while maintaining all automation features.
"""

import asyncio
import json
import logging
import secrets
import string
from pathlib import Path
from typing import Dict, Any, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from ..core.config import config
from ..services.database_service import DatabaseService
from ..services.onboarding_service import OnboardingService

logger = logging.getLogger(__name__)
console = Console()

app = typer.Typer(
    name="install-solution",
    help="Install and setup new FBS solutions with Odoo integration"
)

@app.command()
def install_solution(
    solution_name: str = typer.Argument(..., help="Name of the solution to install"),

    # Odoo connection parameters
    odoo_url: Optional[str] = typer.Option(None, help="Odoo server URL"),
    odoo_database: Optional[str] = typer.Option(None, help="Odoo database name"),
    odoo_username: Optional[str] = typer.Option(None, help="Odoo username"),
    odoo_password: Optional[str] = typer.Option(None, help="Odoo password"),

    # Module installation
    modules: Optional[str] = typer.Option(None, help="Comma-separated list of Odoo modules to install"),

    # Admin configuration
    admin_email: Optional[str] = typer.Option(None, help="Admin user email"),
    admin_password: Optional[str] = typer.Option(None, help="Admin user password"),

    # Configuration file
    config_file: Optional[str] = typer.Option(None, help="Configuration file path"),

    # Flags
    skip_odoo_setup: bool = typer.Option(False, help="Skip Odoo database setup"),
    skip_django_setup: bool = typer.Option(False, help="Skip Django database setup"),
    force: bool = typer.Option(False, help="Force installation even if solution exists")
):
    """
    Install and setup new FBS solutions with Odoo integration.

    PRESERVES Django management command functionality with async improvements.
    """
    try:
        # Display installation header
        console.print()
        console.print(Panel.fit(
            f"[bold blue]🚀 FBS Solution Installation[/bold blue]\n"
            f"[cyan]Solution:[/cyan] {solution_name}",
            title="Installation Started"
        ))

        # Load configuration from file if provided
        if config_file:
            config_data = _load_config_file(config_file)
            odoo_url = odoo_url or config_data.get('odoo_url')
            odoo_database = odoo_database or config_data.get('odoo_database')
            odoo_username = odoo_username or config_data.get('odoo_username')
            odoo_password = odoo_password or config_data.get('odoo_password')
            modules = modules or config_data.get('modules')
            admin_email = admin_email or config_data.get('admin_email')
            admin_password = admin_password or config_data.get('admin_password')

        # Validate required parameters
        if not skip_odoo_setup and not all([odoo_url, odoo_database, odoo_username, odoo_password]):
            console.print("[red]❌ Error:[/red] Odoo URL, database, username, and password are required when not skipping Odoo setup")
            raise typer.Exit(1)

        # Generate admin credentials if not provided
        if not admin_email:
            admin_email = f'admin@{solution_name}.com'

        if not admin_password:
            admin_password = _generate_secure_password()
            console.print(f"[yellow]🔐 Generated secure admin password:[/yellow] [bold]{admin_password}[/bold]")
            console.print("[yellow]💡 Save this password securely![/yellow]")

        # Parse modules
        module_list = []
        if modules:
            module_list = [module.strip() for module in modules.split(',')]

        # Run installation
        result = asyncio.run(_install_solution_async(
            solution_name=solution_name,
            odoo_url=odoo_url,
            odoo_database=odoo_database,
            odoo_username=odoo_username,
            odoo_password=odoo_password,
            modules=module_list,
            admin_email=admin_email,
            admin_password=admin_password,
            skip_odoo_setup=skip_odoo_setup,
            skip_django_setup=skip_django_setup
        ))

        if result['success']:
            _display_success_summary(result)
        else:
            _display_error_summary(result)

    except Exception as e:
        logger.error(f"Installation failed: {e}")
        console.print(f"[red]❌ Installation failed:[/red] {str(e)}")
        raise typer.Exit(1)

async def _install_solution_async(
    solution_name: str,
    odoo_url: str,
    odoo_database: str,
    odoo_username: str,
    odoo_password: str,
    modules: list,
    admin_email: str,
    admin_password: str,
    skip_odoo_setup: bool,
    skip_django_setup: bool
) -> Dict[str, Any]:
    """
    Async installation logic - PRESERVED from Django management command
    """
    result = {
        'success': False,
        'solution_name': solution_name,
        'steps_completed': [],
        'errors': [],
        'databases': {},
        'modules_installed': [],
        'modules_skipped': [],
        'modules_failed': [],
        'admin_created': False
    }

    try:
        # Initialize services
        database_service = DatabaseService(solution_name)
        onboarding_service = OnboardingService()

        # Step 1: Create databases
        console.print("\n[cyan]📊 Step 1: Creating Databases[/cyan]")

        if not skip_django_setup:
            console.print("  Creating Django database...")
            django_result = await database_service.create_database('django', solution_name)
            if django_result['success']:
                result['databases']['django'] = django_result['database_name']
                result['steps_completed'].append('django_database_created')
                console.print(f"  [green]✅ Django database created:[/green] {django_result['database_name']}")
            else:
                result['errors'].append(f"Django database creation failed: {django_result.get('error')}")
                console.print(f"  [yellow]⚠️  Django database warning:[/yellow] {django_result.get('error')}")

        if not skip_odoo_setup:
            console.print("  Creating Odoo database...")
            odoo_result = await database_service.create_database('fbs', solution_name)
            if odoo_result['success']:
                result['databases']['odoo'] = odoo_result['database_name']
                result['steps_completed'].append('odoo_database_created')
                console.print(f"  [green]✅ Odoo database created:[/green] {odoo_result['database_name']}")
            else:
                result['errors'].append(f"Odoo database creation failed: {odoo_result.get('error')}")
                console.print(f"  [yellow]⚠️  Odoo database warning:[/yellow] {odoo_result.get('error')}")

        # Step 2: Setup Odoo if not skipped
        if not skip_odoo_setup:
            console.print("\n[cyan]🔗 Step 2: Setting up Odoo[/cyan]")

            # Test Odoo connection
            console.print("  Testing Odoo connection...")
            from ..services.odoo_service import OdooService
            odoo_service = OdooService(solution_name)
            odoo_service.configure_connection(odoo_url, odoo_database, odoo_username, odoo_password)

            health_check = await odoo_service.health_check()
            if health_check['status'] == 'healthy':
                console.print("  [green]✅ Odoo connection successful[/green]")

                # Install modules
                if modules:
                    console.print(f"  Installing {len(modules)} modules...")
                    for module in modules:
                        console.print(f"    Installing {module}...")
                        # Implement module installation
                        try:
                            # Install module via Odoo
                            from ..services.odoo_service import OdooService
                            odoo_service = OdooService(solution_name)

                            # Check if module exists and install it
                            module_info = await odoo_service.get_module_info(module)
                            if module_info and module_info.get('state') != 'installed':
                                install_result = await odoo_service.install_module(module)
                                if install_result['success']:
                                    result['modules_installed'].append(module)
                                    console.print(f"    [green]✅ Module {module} installed[/green]")
                                else:
                                    console.print(f"    [red]❌ Failed to install module {module}: {install_result.get('error', 'Unknown error')}[/red]")
                            else:
                                result['modules_skipped'].append(module)
                                console.print(f"    [yellow]⚠️ Module {module} already installed or not found[/yellow]")

                        except Exception as e:
                            console.print(f"    [red]❌ Error installing module {module}: {str(e)}[/red]")
                            result['modules_failed'].append(module)

                # Create admin user
                console.print("  Creating admin user...")
                # Implement admin user creation
                try:
                    from ..services.auth_service import AuthService
                    auth_service = AuthService(solution_name)

                    # Create admin user with default credentials
                    admin_data = {
                        'username': 'admin',
                        'email': 'admin@fbs.local',
                        'password': 'admin123',  # This should be changed after first login
                        'role': 'admin',
                        'is_active': True
                    }

                    user_result = await auth_service.create_admin_user(admin_data)
                    if user_result['success']:
                        result['admin_created'] = True
                        result['admin_username'] = admin_data['username']
                        console.print(f"    [green]✅ Admin user '{admin_data['username']}' created[/green]")
                        console.print("    [yellow]⚠️ Default password: admin123 (change immediately!)[/yellow]")
                    else:
                        console.print(f"    [red]❌ Failed to create admin user: {user_result.get('error', 'Unknown error')}[/red]")

                except Exception as e:
                    console.print(f"    [red]❌ Error creating admin user: {str(e)}[/red]")
                    result['admin_created'] = False

                result['steps_completed'].append('odoo_setup_completed')
            else:
                result['errors'].append(f"Odoo connection failed: {health_check.get('error')}")
                console.print(f"  [red]❌ Odoo connection failed:[/red] {health_check.get('error')}")

        # Step 3: Setup Django solution
        if not skip_django_setup:
            console.print("\n[cyan]⚙️  Step 3: Setting up Django Solution[/cyan]")

            # Create solution setup wizard
            setup_result = await onboarding_service.create_solution_setup(
                solution_name=solution_name,
                admin_email=admin_email,
                admin_password=admin_password
            )

            if setup_result['success']:
                result['setup_id'] = setup_result.get('setup_id')
                result['steps_completed'].append('django_setup_completed')
                console.print(f"  [green]✅ Solution setup created:[/green] {setup_result['setup_id']}")
            else:
                result['errors'].append(f"Django setup failed: {setup_result.get('error')}")
                console.print(f"  [yellow]⚠️  Solution setup warning:[/yellow] {setup_result.get('error')}")

        # Generate summary
        result['success'] = len(result['errors']) == 0
        result['summary'] = _generate_installation_summary(result)

        return result

    except Exception as e:
        result['errors'].append(str(e))
        return result

def _generate_installation_summary(result: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive installation summary"""
    return {
        'solution_name': result['solution_name'],
        'status': 'completed' if result['success'] else 'failed',
        'steps_completed': result['steps_completed'],
        'databases': result['databases'],
        'admin_email': result.get('admin_email'),
        'odoo_setup': 'odoo_database_created' in result['steps_completed'],
        'django_setup': 'django_setup_completed' in result['steps_completed'],
        'modules_installed': result['modules_installed'],
        'errors': result['errors']
    }

def _display_success_summary(result: Dict[str, Any]):
    """Display successful installation summary"""
    table = Table(title="📋 Installation Summary")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="white")

    table.add_row("Solution Name", "✅", result['solution_name'])
    table.add_row("Databases", "✅", f"Created {len(result['databases'])} databases")

    if result['databases']:
        for db_type, db_name in result['databases'].items():
            table.add_row(f"  {db_type.title()}", "✅", db_name)

    if result['modules_installed']:
        table.add_row("Modules", "✅", f"Installed {len(result['modules_installed'])} modules")
        for module in result['modules_installed']:
            table.add_row("  Module", "✅", module)

    table.add_row("Admin User", "✅", result.get('admin_email', 'N/A'))

    console.print("\n", table)

    # Save summary to file
    summary_file = f"{result['solution_name']}_installation_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(result['summary'], f, indent=2)

    console.print(f"\n[green]💾 Installation summary saved to:[/green] {summary_file}")

    # Success message
    success_text = Text("🎉 Solution installation completed successfully!", style="bold green")
    console.print(f"\n{success_text}")

def _display_error_summary(result: Dict[str, Any]):
    """Display error summary for failed installation"""
    console.print("\n[red]❌ Installation completed with errors[/red]")

    if result['errors']:
        console.print("\n[red]Errors:[/red]")
        for error in result['errors']:
            console.print(f"  • {error}")

    console.print(f"\n[yellow]⚠️  Solution may be partially installed. Check errors above.[/yellow]")

def _load_config_file(config_file: str) -> Dict[str, Any]:
    """Load configuration from file"""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[red]❌ Failed to load config file:[/red] {str(e)}")
        raise typer.Exit(1)

def _generate_secure_password(length: int = 16) -> str:
    """Generate secure random password"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(characters) for _ in range(length))

if __name__ == "__main__":
    app()
