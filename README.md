# pvpc-report

:es:

App para consultar el precio de la luz PVPC en España desde el canal de Telegram [PVPC Report](https://t.me/pvpc_report).

Extrae diariamente los datos del precio de la luz de la [API pública de preciodelaluz.org](https://api.preciodelaluz.org/), realiza unas operaciones de analítica básica y envía la información al canal de Telegram.

La ejecución se realiza pasada la medianoche en España de manera automatizada mediante [Github Actions](https://github.com/DaniSancas/pvpc-report/actions/workflows/daily_message.yml).

---

:gb: 

App to read the PVPC electric tariff from the Telegram channel [PVPC Report](https://t.me/pvpc_report).

Extracts the daily price data from [preciodelaluz.org's public API](https://api.preciodelaluz.org/), performs some basic analytics transformations and sends the information to the Telegram channel.

The execution is triggered after spanish midnight scheduled by [Github Actions](https://github.com/DaniSancas/pvpc-report/actions/workflows/daily_message.yml).
