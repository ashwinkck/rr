import daemon
import sys
import os
import logging
import asyncio
from services.mempool_monitor import run_mempool_daemon

def setup_logging():
    """Setup logging for daemon"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('/tmp/riskrobo_daemon.log'),
            logging.StreamHandler()
        ]
    )

def daemon_main():
    """Main daemon process"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting RiskRobo mempool monitoring daemon")
        asyncio.run(run_mempool_daemon())
    except Exception as e:
        logger.error(f"Daemon error: {e}")
        sys.exit(1)

def start_daemon():
    """Start the daemon process"""
    with daemon.DaemonContext():
        daemon_main()

def stop_daemon():
    """Stop the daemon process"""
    # Read PID file and kill process
    pid_file = '/tmp/riskrobo_daemon.pid'
    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        os.kill(pid, 15)  # SIGTERM
        os.remove(pid_file)
        print("Daemon stopped")
        
    except FileNotFoundError:
        print("Daemon not running")
    except Exception as e:
        print(f"Error stopping daemon: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python daemon_manager.py [start|stop|status]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'start':
        start_daemon()
        print("Daemon started")
    elif command == 'stop':
        stop_daemon()
    elif command == 'status':
        # Check if daemon is running
        pid_file = '/tmp/riskrobo_daemon.pid'
        if os.path.exists(pid_file):
            print("Daemon is running")
        else:
            print("Daemon is not running")
    else:
        print("Unknown command")
        sys.exit(1)
