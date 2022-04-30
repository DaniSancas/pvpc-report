from pvpc.adapter import PrecioLuzInputAdapter, TelegramOutputAdapter
from pvpc.domain import PVPCDay

def main():
    input_repo = PrecioLuzInputAdapter()
    output_repo = TelegramOutputAdapter()

    domain = PVPCDay(input_repo=input_repo, output_repo=output_repo)
    domain.run()

if __name__ == "__main__":
    main()