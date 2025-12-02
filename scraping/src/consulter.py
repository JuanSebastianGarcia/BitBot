import aiohttp
import asyncio
import logging
from typing import Any, List, Optional

class Consulter:
    
    def __init__(self, max_retries: int = 3, timeout: int = 30, max_concurrent: int = 10):
        """
        Initialize the Consulter class.
        
        Args:
            max_retries (int): Maximum number of retry attempts for failed requests
            timeout (int): Request timeout in seconds
            max_concurrent (int): Maximum number of concurrent requests
        """
        self.max_retries = max_retries
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.logger = logging.getLogger(__name__)
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.rigth_request_count = 0
        self.wrong_request_count = 0

    async def fetch_url_with_retry(
        self, 
        session: aiohttp.ClientSession, 
        url: str,
        retry_count: int = 0
    ) -> Optional[dict]:
        """
        Fetch a single URL with retry logic and semaphore control.
        
        Args:
            session (aiohttp.ClientSession): HTTP client session
            url (str): URL to fetch
            retry_count (int): Current retry attempt number
            
        Returns:
            Optional[dict]: JSON response or None if all retries failed
        """
        async with self.semaphore:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        self.rigth_request_count += 1
                        return await response.json()
                    else:
                        self.logger.warning(
                            f"Failed to fetch {url}: Status {response.status}"
                        )
                        
            except asyncio.TimeoutError:
                self.logger.warning(f"Timeout while fetching {url}")
            except aiohttp.ClientError as e:
                self.logger.warning(f"Client error while fetching {url}: {e}")
            except Exception as e:
                self.logger.warning(f"Unexpected error while fetching {url}: {e}")
            
            # Retry logic
            if retry_count < self.max_retries:
                self.logger.info(f"Retrying {url} (attempt {retry_count + 2}/{self.max_retries + 1})")
                await asyncio.sleep(1)  # Wait 1 second before retry
                return await self.fetch_url_with_retry(session, url, retry_count + 1)
            
            self.logger.error(f"All retry attempts failed for {url}")
            self.wrong_request_count += 1
            return None

    async def process_urls(self, session: aiohttp.ClientSession, url_list: List[str]) -> List[dict]:
        """
        Process all URLs concurrently and collect responses.
        
        Args:
            session (aiohttp.ClientSession): HTTP client session
            url_list (List[str]): List of URLs to process
            
        Returns:
            List[dict]: List of JSON responses
        """
        tasks = [
            self.fetch_url_with_retry(session, url) 
            for url in url_list
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=False)
        return [response for response in responses if response is not None]

    async def main(self, url_list: List[str]) -> List[dict]:
        """
        Main method to fetch JSON responses from a list of URLs.
        
        Makes concurrent requests to all URLs using aiohttp.
        Implements retry logic for failed requests.
        
        Args:
            url_list (List[str]): List of URLs to fetch data from
            
        Returns:
            List[dict]: List of JSON responses from successful requests
        """
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            responses = await self.process_urls(session, url_list)
            self.logger.info(f"Right request count: {self.rigth_request_count}")
            self.logger.info(f"Wrong request count: {self.wrong_request_count}")
            return responses
