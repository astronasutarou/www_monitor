# Classical Website Monitor
This project provides a simple script to monitor updates of a static website.


## Dependences
- &ge;python2.7
- modules: argparse, requests, hashlib, logging, time

## Usage
```
usage: cwwwm.py [-h] [--title TITLE] [--interval INTERVAL] [--slack SLACK]
                [--debug]
                url

classical website monitoring tool

positional arguments:
  url                  url of the website to be monitored

optional arguments:
  -h, --help           show this help message and exit
  --title TITLE        title of the website
  --interval INTERVAL  monitoring interval in seconds
  --hook HOOK          the path to a hook command
  --debug              enabling debug outputs
```

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.
