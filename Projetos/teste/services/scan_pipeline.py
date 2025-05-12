from utils.runner import run_tool_async
import logging

async def execute_scan(domain: str):
    logger = logging.getLogger(__name__)
    result = {"target": domain}

    subfinder = await run_tool_async(["subfinder", "-d", domain, "-silent"], "subfinder")
    result["subdomains"] = subfinder.get("output", [])

    if subfinder["status"] == "ok":
        dnsx = await run_tool_async(["dnsx", "-silent"], "dnsx", input_data="\n".join(result["subdomains"]))
        result["resolved"] = dnsx.get("output", [])

        if dnsx["status"] == "ok":
            naabu = await run_tool_async(["naabu", "-silent"], "naabu", input_data="\n".join(result["resolved"]))
            result["open_ports"] = naabu.get("output", [])

            if naabu["status"] == "ok":
                httpx = await run_tool_async(["httpx", "-silent", "-title"], "httpx", input_data="\n".join(result["open_ports"]))
                result["http_services"] = httpx.get("output", [])

                if httpx["status"] == "ok":
                    nuclei = await run_tool_async(["nuclei", "-silent", "-json"], "nuclei", input_data="\n".join(result["http_services"]))
                    result["vulnerabilities"] = nuclei.get("output", [])

    logger.info(f"Scan finalizado para {domain}")
    return result
