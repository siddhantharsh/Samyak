from core.entities import LeakEvent

def normalize_event(event: LeakEvent) -> str:
    """
    Unifies gateway codes, issuer response codes, Mastercard MACs, 
    Visa decline category codes, and NPCI codes into one namespace.
    """
    rc = event.raw_codes
    
    # Priority order for mapping down to a single code
    if rc.npci_code:
        return f"NPCI:{rc.npci_code}"
    if rc.mac:
        return f"MAC:{rc.mac}"
    if rc.network_category:
        return f"NETWORK:{rc.network_category}"
    if rc.issuer_code:
        return f"ISSUER:{rc.issuer_code}"
    if rc.gateway_code:
        return f"GATEWAY:{rc.gateway_code}"
        
    # If no raw codes are present, fallback to the base leak type
    return f"LEAK:{event.leak_type.value}"
