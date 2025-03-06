import os
import mmap
import time
import logging
import concurrent.futures
import psutil
import multiprocessing 
from typing import List, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %z'
)

CHUNK_SIZE = 4 * 1024 * 1024 * 1024 
RESULT_FOLDER = "results"  

class LargeTextSearcher:
    def __init__(self, upload_folder: str, chunk_size: int = CHUNK_SIZE, max_ram_usage: int = 13 * 1024 * 1024 * 1024):
        self.upload_folder = upload_folder
        self.chunk_size = chunk_size
        self.max_ram_usage = max_ram_usage 

        if not os.path.exists(RESULT_FOLDER):
            os.makedirs(RESULT_FOLDER)

    def search_worker(self, file_path: str, start_position: int, end_position: int, filter_bytes: bytes) -> Tuple[List[str], int]:
        results = []
        chunk_size = 0
        try:
            with open(file_path, 'rb') as file:
                with mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    mm.seek(start_position)
                    chunk = mm.read(end_position - start_position)
                    chunk_size = len(chunk)
                    lines = chunk.split(b'\n')

                    for line in lines:
                        if filter_bytes in line.lower():
                            results.append(line.decode('utf-8', errors='ignore').strip())

        except Exception as e:
            logging.error(f"Error en search_worker: {e}")
        return results, chunk_size

    async def async_query_files(self, filter_text: str) -> Tuple[List[str], float, int, int]:
        start_time = time.time()
        all_results = []
        total_data_processed = 0
        filter_bytes = filter_text.lower().encode('utf-8', errors='ignore')

        files = [f for f in os.listdir(self.upload_folder) if f.endswith('.txt')]

        for filename in files:
            file_path = os.path.join(self.upload_folder, filename)
            file_size = os.path.getsize(file_path)
            logging.info(f"Processing file: {filename} (size: {file_size // (1024**2)} MB)")

            file_start_time = time.time()

            ram_per_thread = self.chunk_size
            max_threads = min(multiprocessing.cpu_count(), self.max_ram_usage // ram_per_thread)

            with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
                chunk_positions = [(start, min(start + self.chunk_size, file_size))
                                   for start in range(0, file_size, self.chunk_size)]
                futures = [executor.submit(self.search_worker, file_path, start, end, filter_bytes)
                           for start, end in chunk_positions]

                for future in concurrent.futures.as_completed(futures):
                    chunk_results, chunk_size = future.result()
                    all_results.extend(chunk_results)
                    total_data_processed += chunk_size

            file_elapsed_time = time.time() - file_start_time
            logging.info(f"Processed file: {filename} - Time: {file_elapsed_time:.2f} seconds - "
                         f"Size: {total_data_processed // (1024**2)} MB - Results: {len(chunk_results)}")

        elapsed_time = time.time() - start_time
        total_results = len(all_results)
        logging.info(f"Search completed in {elapsed_time:.2f} seconds. Total data processed: "
                     f"{total_data_processed // (1024**2)} MB. Total results: {total_results}")

        self.save_results(filter_text, all_results)

        return all_results, elapsed_time, total_data_processed, total_results

    def save_results(self, filter_text: str, results: List[str]):
        file_name = os.path.join(RESULT_FOLDER, f"{filter_text}.txt")
        with open(file_name, 'w', encoding='utf-8') as f:
            for line in results:
                f.write(line + '\n')
        logging.info(f"Results saved in: {file_name}")
