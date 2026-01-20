import os
import requests
import logging

logger = logging.getLogger(__name__)

def get_secret(name: str, default: str | None = None) -> str | None:
    """Fetch secret by name.

    Order of resolution:
    1. Environment variable with the exact name
    2. HashiCorp Vault (if VAULT_ADDR + VAULT_TOKEN configured) at secret/data/{name}
    3. Return default
    """
    # 1) env
    val = os.getenv(name)
    if val:
        return val

    # 2) Vault
    vault_addr = os.getenv("VAULT_ADDR")
    vault_token = os.getenv("VAULT_TOKEN")
    if vault_addr and vault_token:
        try:
            url = f"{vault_addr.rstrip('/')}/v1/secret/data/{name}"
            headers = {"X-Vault-Token": vault_token}
            r = requests.get(url, headers=headers, timeout=5)
            r.raise_for_status()
            data = r.json()
            # KV v2 stores secret under data.data
            return data.get("data", {}).get("data", {}).get(name) or data.get("data", {}).get("value")
        except Exception as e:
            logger.warning("Vault lookup failed for %s: %s", name, e)

    return default
