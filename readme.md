# Registration helper on https://portal.mozgo.com/

After login you will be able to choose one of your teams, city shown in brackets. Then enter number of players (from 2 to 10). Finally you should choose a preferred game.

## Usage example

```python
import time
from mozgo_registration import Mozgo

mozgo_session = Mozgo(login, password)

while mozgo_session.register_to_game() != 201:
    time.sleep(1)
    mozgo_session.register_to_game()
```