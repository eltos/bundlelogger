# bundlelogger
An extension for python's logging module that bundles frequently recurring but equal log messages

## Example Output
    14,746 INFO: 1234 errors following, long pause after #204
    14,747 ERROR: fail
    14,762 ERROR: fail
    14,775 ERROR: fail
    14,789 ERROR: fail
    14,803 ERROR: fail
    14,875 ERROR: [10 repetitions] fail
    15,076 ERROR: [20 repetitions] fail
    15,505 ERROR: [50 repetitions] fail
    16,280 ERROR: [100 repetitions] fail
    17,723 ERROR: [200 repetitions] fail
    17,813 ERROR: [204 repetitions] fail
    37,073 ERROR: [500 repetitions] fail
    44,127 ERROR: [1000 repetitions] fail
    47,466 ERROR: [1234 repetitions] fail
    47,480 INFO: Test completed
        
## Usage
```python  
import logging
from bundlelogger import BundleLogger

logging.Logger.manager.setLoggerClass(BundleLogger)
```
