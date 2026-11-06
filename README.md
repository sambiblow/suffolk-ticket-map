# Where Western Suffolk Gets Ticketed

Interactive map of traffic tickets by road in Babylon, Brookhaven, Huntington, Islip and Smithtown (Suffolk County, NY), January 2024 to October 2026.

**Live map:** https://sambiblow.github.io/suffolk-ticket-map/

![Map preview](suffolk_ticket_roads.png)

## What it shows
- Every road with at least one ticket, colored yellow (few) to red (most) on a log scale
- A switch for all years, 2024, 2025 and 2026
- Stats for each period: busiest roads, busiest day and month, tickets per 1,000 residents by town

## How it works
1. Ticket locations are typed by hand, so each one is cleaned into a standard road name (removing direction notes, cross streets and house numbers, and combining spellings like "LIE", "I 495" and "W/B 495").
2. Census road lines are cut at town borders.
3. Each ticket is matched to a road with the same name in the same town. 95.6% of tickets were matched.

## Data
- Ticket data: provided by the project sponsor (not included in this repo)
- Roads and town borders: U.S. Census Bureau TIGER/Line 2024

## Tools
Python (pandas, geopandas, matplotlib, folium)

Business Analytics Capstone, Farmingdale State College, Fall 2026
