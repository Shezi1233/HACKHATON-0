from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import shutil
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class DropFolderHandler(FileSystemEventHandler):
    def __init__(self, vault_path: str):
        self.needs_action = Path(vault_path) / 'Needs_Action'
        self.logger = logging.getLogger(self.__class__.__name__)

    def on_created(self, event):
        if event.is_directory:
            return
        source = Path(event.src_path)
        # Only process non-markdown files by creating a notification
        if source.suffix.lower() != '.md':
            dest = self.needs_action / f'FILE_DROP_{source.name}'
            # Copy file or create notification
            self.create_metadata(source, dest)
        else:
            # For markdown files, just create a notification
            self.create_metadata(source, self.needs_action / f'NEW_MD_FILE_{source.name}')

    def create_metadata(self, source: Path, dest: Path):
        meta_path = dest.with_suffix('.md')
        meta_path.write_text(f'''---
type: file_drop
original_name: {source.name}
size: {source.stat().st_size}
timestamp: {time.time()}
---

New file dropped for processing: **{source.name}**

Original path: `{source}`
File size: {source.stat().st_size} bytes

Please review this file and take appropriate action.
''')
        self.logger.info(f'Created action file: {meta_path}')


class FileSystemWatcher:
    def __init__(self, vault_path: str, watch_folder: str = None):
        self.vault_path = Path(vault_path)
        self.watch_folder = Path(watch_folder) if watch_folder else self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.logger = logging.getLogger(self.__class__.__name__)

    def run(self):
        self.logger.info(f'Starting file system watcher for: {self.watch_folder}')

        # Create observer
        event_handler = DropFolderHandler(str(self.vault_path))
        observer = Observer()
        observer.schedule(event_handler, str(self.watch_folder), recursive=False)

        # Create needed directories
        self.needs_action.mkdir(exist_ok=True)

        observer.start()
        self.logger.info(f'File watcher started. Monitoring: {self.watch_folder}')

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            self.logger.info('File watcher stopped by user')

        observer.join()


if __name__ == "__main__":
    # Example usage - you would call this with your vault path
    import sys
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = "./AI_Employee_Vault"  # Default path

    watcher = FileSystemWatcher(vault_path)
    watcher.run()