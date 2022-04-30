import sys

from pvpc.adapter import PrecioLuzInputAdapter, TelegramOutputAdapter
from pvpc.domain import PVPCDay

def main(token: str, channel: str):
    input_repo = PrecioLuzInputAdapter()
    output_repo = TelegramOutputAdapter(token=token, channel=channel)

    domain = PVPCDay(input_repo=input_repo, output_repo=output_repo)
    domain.run()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise Exception(
            f"Less arguments ({len(sys.argv) - 1}) than expected. "
            "Expected `token` and `channel` strings."
        )
    main(token=sys.argv[1], channel=sys.argv[2])