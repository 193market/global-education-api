# Global Education Index API

Global education data including adult literacy rates, school enrollment at all levels, government education spending, pupil-teacher ratios, and country rankings. Powered by World Bank Open Data.

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | API info and available endpoints |
| `GET /summary` | All education indicators for a country |
| `GET /literacy` | Adult literacy rate |
| `GET /enrollment` | School enrollment (primary/secondary/tertiary) |
| `GET /spending` | Government education spending (% of GDP) |
| `GET /pupil-teacher` | Pupil-teacher ratio in primary schools |
| `GET /completion` | Primary school completion rate |
| `GET /tertiary` | Tertiary education enrollment |
| `GET /literacy-ranking` | Countries ranked by literacy rate |
| `GET /spending-ranking` | Countries ranked by education spending |

## Query Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `country` | ISO3 country code (e.g., USA, FIN, KOR) | `WLD` |
| `limit` | Number of years or countries | `10` |

## Data Source

World Bank Open Data
https://data.worldbank.org/indicator/SE.ADT.LITR.ZS

## Authentication

Requires `X-RapidAPI-Key` header via RapidAPI.
