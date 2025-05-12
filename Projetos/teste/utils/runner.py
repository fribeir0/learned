import asyncio
import logging

async def run_tool_async(command, tool_name, input_data=None):
    logger = logging.getLogger(__name__)
    try:
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdin=asyncio.subprocess.PIPE if input_data else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate(input=input_data.encode() if input_data else None)
        if proc.returncode == 0:
            output = stdout.decode().strip().split("\n")
            logger.info(f"{tool_name} finalizado com sucesso.")
            return {"status": "ok", "output": output}
        else:
            logger.error(f"{tool_name} falhou: {stderr.decode().strip()}")
            return {"status": "error", "error": stderr.decode().strip(), "output": []}
    except Exception as e:
        logger.exception(f"{tool_name} falhou com exceção.")
        return {"status": "exception", "error": str(e), "output": []}
