from endpoint_generator import EndpointGenerator
from consulter import Consulter
from procesor import Procesor
from save import Saver
import logging
import asyncio
from datetime import datetime
from calculator_data import CalculatorData

logging.basicConfig(level=logging.INFO)
class Main:

    def __init__(self,
        candle_size: int = 1,
        initial_date: datetime = datetime(2024, 1, 1, 1, 0, 0),
        end_date: datetime = datetime(2025, 10, 20, 1, 0, 0),
        percentage_return_threshold: float = 0.05,
        ):
        self.endpoint_generator = EndpointGenerator(initial_date=initial_date, end_date=end_date)
        self.consulter = Consulter()
        self.procesor = Procesor(candle_size=candle_size)
        self.saver = Saver("scraping/data/bitcoin_candles.csv")
        self.calculator_data = CalculatorData(percentage_return_threshold=percentage_return_threshold)
        self.logger = logging.getLogger(__name__)

    async def main(self):
        self.logger.info("Starting the scraping process")
        url_list = self.endpoint_generator.main()
        self.logger.info(f"Generated {len(url_list)} endpoints")
        responses = await self.consulter.main(url_list)
        self.logger.info(f"Received {len(responses)} responses")
        processed_data = self.procesor.main(responses)
        self.logger.info(f"Processed {len(processed_data)} candles")
        calculated_data = self.calculator_data.main(processed_data)
        self.logger.info(f"Calculated {len(calculated_data)} candles")
        self.saver.main(calculated_data)
        self.logger.info("Scraping process completed successfully")
        

if __name__ == "__main__":
    main = Main()
    asyncio.run(main.main())