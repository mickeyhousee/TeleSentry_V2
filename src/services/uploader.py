import logging
import aiohttp


async def upload_file_to_api(file_path: str, api_url: str) -> None:
    """
    Upload a file to the external API endpoint.
    """
    try:
        async with aiohttp.ClientSession() as session:
            with open(file_path, "rb") as file_handle:
                files = {"file": file_handle}
                async with session.post(api_url, data=files) as response:
                    if response.status == 200:
                        logging.info("File %s uploaded successfully", file_path)
                    else:
                        logging.error("Failed to upload %s. Status code: %s", file_path, response.status)
    except Exception as exc:  # pragma: no cover - defensive logging
        logging.error("Error uploading file %s to API: %s", file_path, exc)

