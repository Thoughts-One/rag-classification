import argparse
import asyncio
from pathlib import Path
from typing import Dict, List, Union, Any
import httpx
from dotenv import load_dotenv
import os

class ClassificationClient:
    """Client for interacting with the RAG classification service."""
    
    def __init__(self, base_url: str, api_key: str):
        """Initialize the client with base URL and API key.
        
        Args:
            base_url: Base URL of the classification service
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.client = httpx.AsyncClient()
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
        
    async def classify_document(
        self,
        content: str,
        title: str = "Untitled",
        source: str = "local",
        role: str = "ASK"
    ) -> Dict[str, Any]:
        """Classify a single document.
        
        Args:
            content: Document content to classify
            title: Document title (default: "Untitled")
            source: Document source (default: "local")
            role: Document role (default: "ASK")
            
        Returns:
            Classification result as a dictionary
        """
        document = {
            "content": content,
            "title": title,
            "source": source,
            "role": role
        }
        return await self._send_request("/api/v1/classify/document", document)
        
    async def classify_batch(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Classify multiple documents in a batch.
        
        Args:
            documents: List of document dictionaries with keys:
                      content, title, source, role
                      
        Returns:
            List of classification results
        """
        return await self._send_request("/api/v1/classify/batch", documents)
        
    async def _send_request(
        self,
        endpoint: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> Any:
        """Internal method to send HTTP requests.
        
        Args:
            endpoint: API endpoint to call
            data: Request payload
            
        Returns:
            Parsed JSON response
            
        Raises:
            httpx.HTTPStatusError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            response = await self.client.post(
                url,
                json=data,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"API request failed: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            print(f"Request failed: {str(e)}")
            raise
            
    async def process_file(self, file_path: str) -> Dict:
        """Process a single file and return classification result.
        
        Args:
            file_path: Path to file to process
            
        Returns:
            Classification result dictionary
            
        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file can't be read
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            content = path.read_text(encoding='utf-8')
            return await self.classify_document(
                content=content,
                title=path.name,
                source=str(path.parent)
            )
        except Exception as e:
            print(f"Failed to process file {file_path}: {str(e)}")
            raise
            
    async def process_directory(
        self, 
        dir_path: str, 
        recursive: bool = True
    ) -> List[Dict]:
        """Process all files in a directory and return classification results.
        
        Args:
            dir_path: Path to directory to process
            recursive: Whether to process subdirectories (default: True)
            
        Returns:
            List of classification results
            
        Raises:
            FileNotFoundError: If directory doesn't exist
        """
        path = Path(dir_path)
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")
            
        documents = []
        pattern = "**/*" if recursive else "*"
        
        for file_path in path.glob(pattern):
            if file_path.is_file():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    documents.append({
                        "content": content,
                        "title": file_path.name,
                        "source": str(file_path.parent),
                        "role": "ASK"
                    })
                except Exception as e:
                    print(f"Skipping file {file_path}: {str(e)}")
                    
        if not documents:
            print(f"No valid files found in {dir_path}")
            return []
            
        return await self.classify_batch(documents)

async def main():
    """Command line interface for the classification client.
    
    Note: Requires Python 3.9+ and the httpx package installed.
    The service runs in a containerized environment on Render.com.
    """
    parser = argparse.ArgumentParser(
        description="RAG Classification Client"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to a single file to classify"
    )
    parser.add_argument(
        "--directory",
        type=str,
        help="Path to directory containing files to classify"
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Process directories recursively (default: True)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        required=False,
        help="API key for authentication (can also be set in .env as API_KEY)"
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="https://rag-classification.onrender.com",
        help="Base URL of classification service"
    )
    
    args = parser.parse_args()
    
    if not args.file and not args.directory:
        parser.error("Either --file or --directory must be specified")

    # Load API key from either command line or .env file
    api_key = args.api_key
    if not api_key:
        load_dotenv()
        api_key = os.getenv("API_KEY")
        if not api_key:
            parser.error("API key is required. Either provide --api-key or set API_KEY in .env file")
            
    async with ClassificationClient(args.base_url, api_key) as client:
        if args.file:
            try:
                result = await client.process_file(args.file)
                print("Classification result:")
                print(result)
            except Exception as e:
                print(f"Failed to process file: {str(e)}")
        elif args.directory:
            try:
                results = await client.process_directory(
                    args.directory,
                    args.recursive
                )
                print(f"Processed {len(results)} documents:")
                for result in results:
                    print(result)
            except Exception as e:
                print(f"Failed to process directory: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())