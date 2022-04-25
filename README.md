# h

hi yes this is the shitcode of bolb bot.
have fun.

written by [koala#9712](https://github.com/koala9712), [Sham#0002](https://github.com/realShamlol) and [ooliver1](<https://github.com/ooliver> 1) ofc

## Deploying

```bash
git clone https://github.com/koala9712/bolb-bot
cd bolb-bot
echo "TOKEN=yourbottoken" > .env
docker-compose up --build -d
```

### Db schema

```bash
poetry/pip install ooliver-botbase
botbase <db-url>
psql mydb
> CREATE TABLE bolb (
    id BIGINT PRIMARY KEY,
    bolbs INT,
    daily TIMESTAMPTZ,
    weekly TIMESTAMPTZ
);
CREATE TABLE
# TODO: script for that
```
