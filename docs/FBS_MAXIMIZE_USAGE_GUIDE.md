# FBS FastAPI v3.1.0 - Complete Suite Usage Guide

## 🎯 **Maximizing FBS Suite: Discovery + Generation + DMS + Licensing**

This guide shows how to maximize the complete FBS FastAPI suite by leveraging all four core components working together: **Discovery**, **Module Generation**, **DMS**, and **License Management**.

---

## 📊 **FBS Suite Component Overview**

### **1. Discovery Service** 🔍
**Purpose**: Explore and understand existing Odoo structures
**Key Capabilities**:
- Discover models, fields, workflows, and relationships
- Install/uninstall modules in Odoo databases
- Analyze existing business logic and data structures
- Provide foundation for extension planning

### **2. Module Generation Service** 🏗️
**Purpose**: Create structured, production-ready Odoo extensions
**Key Capabilities**:
- Generate complete Odoo modules with inheritance
- Create models, fields, workflows, views, and security
- Support pure backend modules (no redundant XML views)
- Generate and install modules automatically

### **3. Document Management System (DMS)** 📄
**Purpose**: Complete document lifecycle management
**Key Capabilities**:
- Document upload, storage, and retrieval
- Workflow-based document approvals
- Version control and audit trails
- Security and access control
- Integration with generated modules

### **4. License Management** 🔐
**Purpose**: Enterprise-grade licensing and feature control
**Key Capabilities**:
- Feature activation/deactivation based on licenses
- Usage limits and quota management
- Multi-tenant license isolation
- Upgrade prompts and license validation

---

## 🚀 **MAXIMIZATION STRATEGIES**

### **Strategy 1: Complete Business Solution Workflow**

#### **Phase 1: Discovery & Planning**
```python
# Initialize FBS Suite
from fbs_fastapi.services.service_interfaces import FBSInterface
fbs = FBSInterface(solution_name="my_business", license_key="enterprise")

# 1. Discover existing Odoo structures
models = await fbs.discovery.discover_models("fbs_my_business_db")
fields = await fbs.discovery.discover_fields("res.partner")
workflows = await fbs.discovery.discover_workflows("sale.order")

print(f"Found {len(models['data']['models'])} existing models")
```

#### **Phase 2: Generate Custom Extensions**
```python
# 2. Generate extensions based on discovery
extensions_spec = {
    "name": "business_extensions",
    "description": "Custom business extensions",
    "models": [{
        "name": "res.partner",
        "inherit_from": "res.partner",
        "fields": [
            {"name": "loyalty_tier", "type": "selection",
             "selection": "[('bronze','Bronze'),('silver','Silver'),('gold','Gold')]"},
            {"name": "credit_limit", "type": "float"},
            {"name": "special_notes", "type": "text"}
        ]
    }, {
        "name": "sale.order",
        "inherit_from": "sale.order",
        "fields": [
            {"name": "custom_discount", "type": "float"},
            {"name": "approval_required", "type": "boolean"}
        ]
    }],
    "workflows": [{
        "model": "sale.order",
        "states": [
            {"name": "draft", "string": "Draft"},
            {"name": "manager_approval", "string": "Manager Approval"},
            {"name": "approved", "string": "Approved"}
        ],
        "transitions": [
            {"from": "draft", "to": "manager_approval", "condition": "amount_total > 5000"},
            {"from": "manager_approval", "to": "approved", "signal": "approve"}
        ]
    }],
    "security": {
        "rules": [
            {"name": "Sales Manager Access", "model": "sale.order",
             "groups": ["sales_manager"], "permissions": ["read", "write", "create"]}
        ]
    }
}

# Generate and install
result = await fbs.module_gen.generate_and_install(extensions_spec, "admin", "my_business")
```

#### **Phase 3: DMS Integration**
```python
# 3. Set up document management for generated models
from fbs_fastapi.services.dms_service import DocumentService

dms = DocumentService("my_business")

# Create document types for generated models
await dms.create_document_type({
    "name": "Contract",
    "description": "Customer contracts",
    "allowed_extensions": ["pdf", "docx"],
    "max_file_size": 10 * 1024 * 1024
})

# Upload documents related to generated records
contract_doc = await dms.create_document({
    "name": "Enterprise Contract",
    "title": "Master Service Agreement",
    "document_type_id": contract_type_id,
    "category_id": business_category_id,
    "confidentiality_level": "confidential"
}, "sales_manager", uploaded_file)
```

#### **Phase 4: License Integration**
```python
# 4. Apply licensing controls
license_info = await fbs.get_license_info()

# Check feature access before enabling advanced features
if await fbs.license.check_feature_access("my_business", "advanced_workflows"):
    # Enable advanced workflow features
    await fbs.workflows.create_advanced_workflow(workflow_config)
else:
    # Fallback to basic workflows
    await fbs.workflows.create_basic_workflow(basic_config)
```

### **Strategy 2: Integrated Discovery-to-Production Pipeline**

#### **Automated Extension Generation**
```python
# Complete automated workflow
result = await fbs.discover_and_extend("admin", "my_business")

# This automatically:
# 1. Discovers all models in fbs_my_business_db
# 2. Generates extension modules for discovered models
# 3. Adds standard business fields (loyalty, custom fields, etc.)
# 4. Creates security rules
# 5. Installs modules in the database
```

#### **Hybrid Extension Approach**
```python
# Combine immediate virtual fields with structured generation
hybrid_result = await fbs.hybrid_extension_workflow(
    "res.partner",
    custom_fields=[
        {"name": "immediate_field", "type": "char"},
        {"name": "urgent_field", "type": "boolean"}
    ],
    user_id="developer",
    tenant_id="my_business"
)

# This provides:
# - Immediate virtual fields for development
# - Structured module generation for production
```

### **Strategy 3: DMS-Powered Module Generation**

#### **Document-Centric Module Generation**
```python
# Generate modules with built-in DMS integration
dms_spec = {
    "name": "document_centric_module",
    "description": "Module with integrated document management",
    "models": [{
        "name": "business.contract",
        "description": "Business contracts with DMS integration",
        "fields": [
            {"name": "contract_number", "type": "char", "required": True},
            {"name": "signed_date", "type": "date"},
            {"name": "contract_file", "type": "binary"},  # For DMS storage
            {"name": "approval_status", "type": "selection",
             "selection": "[('draft','Draft'),('approved','Approved'),('signed','Signed')]"}
        ],
        "methods": [{
            "name": "upload_contract_file",
            "body": """
                # Integration with DMS
                if self.contract_file:
                    dms_result = await self.env['dms.document'].create({
                        'name': f'Contract {self.contract_number}',
                        'attachment': self.contract_file,
                        'res_model': 'business.contract',
                        'res_id': self.id
                    })
                    self.contract_file_dms_id = dms_result.id
            """
        }]
    }],
    "workflows": [{
        "model": "business.contract",
        "states": [
            {"name": "draft", "string": "Draft"},
            {"name": "document_upload", "string": "Document Uploaded"},
            {"name": "approved", "string": "Approved"},
            {"name": "signed", "string": "Signed"}
        ]
    }],
    "security": {
        "rules": [{
            "name": "Contract Access",
            "model": "business.contract",
            "permissions": ["read"]
        }, {
            "name": "Contract Management",
            "model": "business.contract",
            "groups": ["contract_managers"],
            "permissions": ["read", "write", "create", "unlink"]
        }]
    }
}

# Generate module with DMS integration
contract_module = await fbs.module_gen.generate_and_install(dms_spec, "admin", "my_business")
```

---

## 🎯 **MAXIMUM VALUE INTEGRATION PATTERNS**

### **Pattern 1: Enterprise Document Workflow**

```python
# Complete document-driven business process
async def create_enterprise_contract_workflow(client_data, contract_file):
    # 1. Check license for advanced features
    if not await fbs.license.check_feature_access("enterprise", "advanced_dms"):
        raise HTTPException(403, "Advanced DMS features not licensed")

    # 2. Create business record with generated module
    contract_record = await fbs.odoo.create_record("business.contract", {
        "contract_number": client_data["contract_number"],
        "client_name": client_data["client_name"],
        "contract_value": client_data["value"]
    })

    # 3. Upload document via DMS
    document = await fbs.dms.create_document({
        "name": f"Contract {client_data['contract_number']}",
        "title": f"Enterprise Contract - {client_data['client_name']}",
        "document_type_id": enterprise_contract_type_id,
        "category_id": legal_category_id,
        "confidentiality_level": "confidential",
        "expiry_date": client_data.get("expiry_date"),
        "metadata": {
            "contract_value": client_data["value"],
            "client_id": client_data["client_id"],
            "generated_module": "business.contract"
        }
    }, "legal_admin", contract_file)

    # 4. Link document to business record
    await fbs.odoo.update_record("business.contract", contract_record["id"], {
        "document_id": document["id"]
    })

    # 5. Start approval workflow
    workflow_instance = await fbs.workflows.start_workflow(
        "contract_approval_workflow",
        {"contract_id": contract_record["id"], "document_id": document["id"]}
    )

    return {
        "contract": contract_record,
        "document": document,
        "workflow": workflow_instance,
        "integrated_services": ["odoo", "dms", "workflows", "license"]
    }
```

### **Pattern 2: Discovery-Driven Customization**

```python
# Use discovery to customize solutions dynamically
async def customize_solution_from_discovery(tenant_id, customization_requirements):
    # 1. Discover existing tenant setup
    existing_models = await fbs.discovery.discover_models(f"fbs_{tenant_id}_db")
    existing_fields = {}

    for model in existing_models["data"]["models"]:
        fields = await fbs.discovery.discover_fields(model["model"])
        existing_fields[model["model"]] = fields["data"]["fields"]

    # 2. Analyze customization requirements
    required_extensions = analyze_requirements(customization_requirements, existing_fields)

    # 3. Generate custom modules based on analysis
    custom_modules = []
    for extension in required_extensions:
        module_spec = generate_custom_module_spec(extension, existing_fields)
        result = await fbs.module_gen.generate_and_install(module_spec, "system", tenant_id)
        custom_modules.append(result)

    # 4. Set up DMS for new modules
    for module in custom_modules:
        await setup_dms_for_module(module, fbs.dms)

    # 5. Configure licensing for new features
    await fbs.license.configure_tenant_features(tenant_id, required_extensions)

    return {
        "tenant_id": tenant_id,
        "custom_modules": custom_modules,
        "dms_configured": True,
        "license_updated": True,
        "discovery_driven": True
    }
```

### **Pattern 3: Multi-Tenant SaaS Platform**

```python
# Complete SaaS tenant onboarding with all FBS services
async def onboard_saas_tenant(tenant_config):
    tenant_id = tenant_config["tenant_id"]
    business_type = tenant_config["business_type"]

    # 1. License validation
    license_valid = await fbs.license.validate_tenant_license(tenant_id, "enterprise")
    if not license_valid:
        raise HTTPException(403, "Invalid or expired license")

    # 2. Database setup
    db_result = await fbs.database.create_tenant_database(tenant_id)

    # 3. Discovery of base business models
    base_models = await fbs.discovery.discover_models("fbs_system_db")

    # 4. Generate tenant-specific customizations
    tenant_modules = await generate_tenant_modules(
        tenant_id, business_type, base_models["data"]["models"]
    )

    # 5. Install generated modules
    installed_modules = []
    for module_spec in tenant_modules:
        result = await fbs.module_gen.generate_and_install(module_spec, "system", tenant_id)
        installed_modules.append(result)

    # 6. Set up DMS structure
    dms_structure = await setup_tenant_dms_structure(tenant_id, business_type, fbs.dms)

    # 7. Configure security and access
    security_config = await setup_tenant_security(tenant_id, tenant_config["user_roles"])

    # 8. Initialize with demo data if requested
    if tenant_config.get("include_demo_data"):
        demo_result = await initialize_demo_data(tenant_id, business_type)

    return {
        "tenant_id": tenant_id,
        "status": "onboarded",
        "modules_installed": len(installed_modules),
        "dms_configured": bool(dms_structure),
        "security_setup": bool(security_config),
        "demo_data_loaded": tenant_config.get("include_demo_data", False),
        "services_integrated": ["discovery", "generation", "dms", "license", "security"]
    }
```

---

## 📈 **PERFORMANCE OPTIMIZATION PATTERNS**

### **Caching Strategy**
```python
# Leverage FBS caching for performance
@fbs.cache.cached(ttl_seconds=300)
async def get_discovered_models(tenant_id):
    return await fbs.discovery.discover_models(f"fbs_{tenant_id}_db")

@fbs.cache.cached(ttl_seconds=600)
async def get_module_templates():
    return await fbs.module_gen.list_templates("system")
```

### **Batch Operations**
```python
# Batch process multiple operations
async def batch_tenant_setup(tenants):
    results = []

    for tenant in tenants:
        # Parallel processing
        discovery_task = asyncio.create_task(fbs.discovery.discover_models(f"fbs_{tenant}_db"))
        license_task = asyncio.create_task(fbs.license.get_tenant_license(tenant))

        discovery_result, license_result = await asyncio.gather(discovery_task, license_task)

        # Generate and install based on discovery
        module_result = await fbs.module_gen.generate_from_discovery(
            discovery_result, "system", tenant
        )

        results.append({
            "tenant": tenant,
            "discovery": discovery_result,
            "license": license_result,
            "modules": module_result
        })

    return results
```

---

## 🔧 **ADVANCED INTEGRATION PATTERNS**

### **Event-Driven Architecture**
```python
# Set up event handlers across services
@fbs.signals.on("module.installed")
async def handle_module_installation(module_info):
    # Automatically set up DMS for new modules
    await fbs.dms.create_document_type_for_module(module_info)

    # Update license usage
    await fbs.license.update_feature_usage("module_generation", +1)

@fbs.signals.on("document.uploaded")
async def handle_document_upload(document_info):
    # Trigger workflow if document requires approval
    if document_info["requires_approval"]:
        await fbs.workflows.start_workflow("document_approval", document_info)

    # Update audit trail
    await fbs.audit.log_activity("document_upload", document_info)
```

### **Microservices Integration**
```python
# Expose FBS services via standardized APIs
@app.get("/api/fbs/health")
async def fbs_health_check():
    """Complete FBS suite health check"""
    health = await fbs.get_system_health()

    # Add cross-service health checks
    health["cross_service_status"] = {
        "discovery_generation_integration": await test_discovery_generation_integration(),
        "dms_license_integration": await test_dms_license_integration(),
        "workflow_dms_integration": await test_workflow_dms_integration()
    }

    return health

@app.post("/api/fbs/execute-workflow")
async def execute_complete_workflow(workflow_request):
    """Execute complete workflow across all FBS services"""
    # 1. Validate license
    # 2. Discover or use existing models
    # 3. Generate required modules
    # 4. Set up DMS structure
    # 5. Execute business workflow
    # 6. Handle document management
    # 7. Update audit trails

    return await fbs.execute_complete_workflow(workflow_request)
```

---

## 🎯 **SUCCESS METRICS & MONITORING**

### **Key Performance Indicators**
```python
# Monitor FBS suite effectiveness
async def get_fbs_metrics():
    return {
        "discovery": {
            "models_discovered": await fbs.discovery.get_discovery_stats(),
            "fields_mapped": await fbs.discovery.get_field_mapping_stats()
        },
        "generation": {
            "modules_generated": await fbs.module_gen.get_generation_stats(),
            "install_success_rate": await fbs.module_gen.get_install_success_rate()
        },
        "dms": {
            "documents_managed": await fbs.dms.get_document_stats(),
            "approval_workflows": await fbs.dms.get_workflow_stats()
        },
        "license": {
            "features_utilized": await fbs.license.get_feature_utilization(),
            "compliance_rate": await fbs.license.get_compliance_stats()
        },
        "integration": {
            "cross_service_calls": await fbs.get_integration_stats(),
            "performance_metrics": await fbs.get_performance_metrics()
        }
    }
```

### **Optimization Recommendations**
```python
# Automatic optimization based on usage patterns
async def optimize_fbs_suite():
    metrics = await get_fbs_metrics()

    recommendations = []

    # Discovery optimization
    if metrics["discovery"]["models_discovered"] > 1000:
        recommendations.append("Implement discovery result caching")

    # Generation optimization
    if metrics["generation"]["install_success_rate"] < 0.95:
        recommendations.append("Review module generation error handling")

    # DMS optimization
    if metrics["dms"]["documents_managed"] > 10000:
        recommendations.append("Consider DMS sharding strategy")

    # License optimization
    if metrics["license"]["compliance_rate"] < 0.99:
        recommendations.append("Review license validation logic")

    return recommendations
```

---

## 📋 **CONCLUSION: MAXIMUM FBS VALUE**

### **Complete Integration Achieved:**
- ✅ **Discovery** explores and understands existing structures
- ✅ **Module Generation** creates structured, production-ready extensions
- ✅ **DMS** provides document lifecycle management
- ✅ **License Management** controls features and usage
- ✅ **Integrated Workflows** combine all services seamlessly

### **Key Benefits Realized:**
1. **Unified Solution**: Single API for complete business suite
2. **Automated Workflows**: Discovery-to-production pipelines
3. **Scalable Architecture**: Multi-tenant, enterprise-ready
4. **Performance Optimized**: Caching, batching, and monitoring
5. **Production Proven**: Comprehensive error handling and logging

### **Usage Pattern Evolution:**
```
Traditional: Manual Odoo customization
FBS v1: Individual service usage
FBS v3.1: Complete integrated suite

From: Discovery → Manual coding → Testing → Deployment
To:   Discovery → Auto-generation → DMS integration → Licensed deployment
```

**The FBS FastAPI v3.1.0 suite provides a complete, integrated business platform that maximizes value through intelligent service orchestration and automated workflows.**
