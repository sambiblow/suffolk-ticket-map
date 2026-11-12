# Where Western Suffolk Gets Ticketed

Interactive maps and charts of 494,248 traffic tickets written in Babylon, Brookhaven, Huntington, Islip and Smithtown (Suffolk County, NY), January 2024 to October 2026.

## Live dashboard
**https://sambiblow.github.io/suffolk-ticket-map/**

All five charts in one page, with a tab for each:

| Tab | What it answers |
|---|---|
| [Road map](https://sambiblow.github.io/suffolk-ticket-map/suffolk_ticket_roads.html) | Which roads get the most tickets? |
| [Crash map](https://sambiblow.github.io/suffolk-ticket-map/crash_map.html) | Where do crash-related tickets happen? |
| [When tickets happen](https://sambiblow.github.io/suffolk-ticket-map/ticket_heatmap.html) | What hours and days are tickets written? |
| [Enforcement vs. crashes](https://sambiblow.github.io/suffolk-ticket-map/crash_vs_tickets.html) | Is enforcement happening when crashes happen? |
| [Multi-ticket stops](https://sambiblow.github.io/suffolk-ticket-map/ticket_sankey.html) | What else gets written once a driver is stopped? |

![Road map preview](suffolk_ticket_roads.png)

## Key findings
- **A few corridors dominate enforcement.** The Long Island Expressway alone accounts for about 20% of all tickets, followed by Sunrise Highway and the Southern State Parkway.
- **Highways have the most crash-related tickets but low crash rates.** The LIE in Brookhaven has 44,224 tickets and a 0.8% crash rate. Some local roads are much higher, such as Frowein Rd (13.8%), Patchogue Yaphank Rd (10.7%) and Nicolls Rd in Islip (9.3%).
- **Enforcement timing does not match crash timing.** 27.8% of tickets are written from 8 to 11 a.m., but only 17.0% of crash-related tickets happen then. From 3 to 6 p.m., crash-related tickets make up 31.4% of the total compared with 26.8% of all tickets.
- **Stops often turn into paperwork checks.** At stops with 2 or more tickets, unlicensed driver is the most common extra ticket, whether the stop began with speeding, a stop sign or tinted windows.
- **Islip writes the most tickets per resident.** Brookhaven has the most tickets overall, but adjusted for population, Islip is highest.

## Charts

### Road map
Every road with at least one ticket, colored yellow (few) to red (most) on a log scale, with a switch for all years, 2024, 2025 and 2026. A side panel shows the busiest roads, busiest day and month, and tickets per 1,000 residents by town.

### Crash map
Every road with at least one crash-related ticket, with two views:
- **Count:** the number of crash-related tickets on each road
- **Crash rate:** the share of a road's tickets written at a crash, shown for roads with 200 or more tickets so small roads do not look extreme

### When tickets happen
A 24-hour by 7-day heatmap with a dropdown for violation type. Each type is shown as a share of its own tickets, so patterns can be compared across types of different sizes. Weekday tickets peak from 8 to 11 a.m. and around 4 to 5 p.m. Speeding is the only type that peaks in the morning.

### Enforcement vs. crashes
Compares the share of all tickets with the share of crash-related tickets by hour and by day of week. Ticketing peaks in the morning and drops on weekends, while crash-related tickets peak in the late afternoon and stay higher on weekends.

### Multi-ticket stops
For the 101,917 stops with 2 or more tickets, shows why each stop happened (left) and what other tickets were written during it (right).

## Method
1. **Road matching.** Ticket locations are typed by hand, so each one is cleaned into a standard road name (removing direction notes, cross streets and house numbers, and combining spellings like "LIE", "I 495" and "W/B 495"). Census road lines are cut at town borders, and each ticket is matched to a road with the same name in the same town. 95.6% of tickets were matched.
2. **Stops.** The data has no stop ID, so tickets with the same date, time, driver birth date and location were treated as one stop.
3. **Crash-related tickets.** Tickets marked ACCIDENT = Y were written at a crash scene. Crash rate is the share of a road's tickets that are crash-related.

## Limitations
- Tickets show where and when police enforced, not how people drive. Roads with little patrol can look safe.
- Crash-related means a ticket written at a crash scene, not every crash. Crash records would make the safety comparison stronger.
- Stops are estimated, since the data has no stop ID.
- 4.4% of tickets could not be matched to a road because their location was too vague.
- October 2026 is a partial month (data ends October 8).

## Files
| File | Description |
|---|---|
| `index.html` | Dashboard with all five charts |
| `ticket_map.ipynb` | Code for the road map |
| `ticket_heatmap.ipynb` | Code for the heatmap, Sankey and crash timing charts |
| `crash_map_cell.py` | Code for the crash map |
| `suffolk_ticket_roads.html` | Interactive road map |
| `crash_map.html` | Interactive crash map |
| `ticket_heatmap.html` | Interactive hour-by-day heatmap |
| `crash_vs_tickets.html` | Interactive enforcement vs. crash timing chart |
| `ticket_sankey.html` | Interactive multi-ticket stop diagram |
| `suffolk_ticket_roads.png` | Static road map |

## Data
- **Ticket data:** provided by the project sponsor. Not included in this repo.
- **Roads and town borders:** U.S. Census Bureau TIGER/Line 2024
- **Town populations:** 2020 U.S. Census

## Tools
Python (pandas, geopandas, matplotlib, folium, plotly), Power BI

To run the code, install the libraries with `pip install pandas geopandas matplotlib folium plotly`. The ticket data file (`ticket_data_clean.zip`) is not public, so it needs to be supplied separately.

---
Business Analytics Capstone, Farmingdale State College, Fall 2026
