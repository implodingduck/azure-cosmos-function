terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=2.62.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "=3.1.0"
    }
  }
  backend "azurerm" {

  }
}

provider "azurerm" {
  features {}

  subscription_id = var.subscription_id
}

locals {
  func_name = "cosmfun${random_string.unique.result}"
}

data "azurerm_client_config" "current" {}

resource "azurerm_resource_group" "rg" {
  name     = "rg-comsos-function-demo"
  location = var.location
}

resource "random_string" "unique" {
  length  = 8
  special = false
  upper   = false
}

resource "azurerm_cosmosdb_account" "db" {
  name                = "${local.func_name}-dba"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  offer_type          = "Standard"
  consistency_policy {
    consistency_level       = "Session"
  }

  geo_location {
    location          = "West US"
    failover_priority = 1
  }

  geo_location {
    location          = azurerm_resource_group.rg.location
    failover_priority = 0
  }
}

resource "azurerm_cosmosdb_sql_database" "db" {
  name                = "${local.func_name}-db"
  resource_group_name = azurerm_cosmosdb_account.db.resource_group_name
  account_name        = azurerm_cosmosdb_account.db.name
  throughput          = 400
}


resource "azurerm_cosmosdb_sql_container" "db" {
  name                  = "${local.func_name}-dbcontainer"
  resource_group_name   = azurerm_cosmosdb_account.db.resource_group_name
  account_name          = azurerm_cosmosdb_account.db.name
  database_name         = azurerm_cosmosdb_sql_database.db.name
  partition_key_path    = "/id"
  partition_key_version = 1
  throughput            = 400
}

data "template_file" "func" {
  template = "${file("${path.module}/function.json.tmpl")}"
  vars = {
    databaseName = "${local.func_name}-db"
    connectionStringSetting = azurerm_cosmosdb_account.db.connection_strings[0]
    collectionName = "${local.func_name}-dbcontainer"
  }
}

resource "local_file" "comsostrigger" {
    sensitive_content     = data.template_file.func.rendered
    filename = "${path.module}/functions/ComsosTrigger/function.json"
}

resource "local_file" "sumcomsostrigger" {
    sensitive_content     = data.template_file.func.rendered
    filename = "${path.module}/functions/SumComsosTrigger/function.json"
}

module "functions" {
  depends_on = [
    local_file.comsostrigger,
    local_file.sumcomsostrigger
  ]
  source = "github.com/implodingduck/tfmodules//functionapp"
  func_name = "${local.func_name}"
  resource_group_name = azurerm_resource_group.rg.name
  resource_group_location = azurerm_resource_group.rg.location
  working_dir = "functions"
  app_settings = {
    "FUNCTIONS_WORKER_RUNTIME" = "python"
    "COSMOSDB_ENDPOINT"        = azurerm_cosmosdb_account.db.endpoint
    "COSMOSDB_KEY"             = azurerm_cosmosdb_account.db.primary_key
    "COSMOSDB_NAME"            = "${local.func_name}-db"
    "COSMOSDB_CONTAINER"       = "${local.func_name}-dbcontainer"
  }
}