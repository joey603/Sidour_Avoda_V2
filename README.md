# Sidour-avoda-Tzora-chevron

## Description
Sidour-avoda-Tzora-chevron is a schedule management application for organizing shifts and work hours. It allows you to create, manage, and optimize worker schedules while respecting various constraints such as minimum rest time between shifts.

## Main Features
- Adding and managing workers
- Automatic generation of optimized schedules
- Verification of minimum rest between shifts (8 hours by default)
- Clear schedule visualization
- Manual assignment modifications
- Evaluation of generated schedule quality
- Saving and loading schedules
- Exporting schedules to CSV format

## Schedule Structure
The application manages three daily time slots:
- Morning: 06:00-14:00
- Afternoon: 14:00-22:00
- Night: 22:00-06:00

## Installation
1. Make sure you have Python installed on your system
2. Clone this repository:
   ```
   git clone https://github.com/your-username/Sidour-avoda-Tzora-chevron.git
   cd Sidour-avoda-Tzora-chevron
   ```
3. Install required dependencies (if necessary)

## Usage
To launch the application, run:
```
python main.py
```

The graphical interface will allow you to:
1. Add workers with their constraints
2. Automatically generate optimized schedules
3. Visualize and modify schedules
4. Save and load existing schedules
5. Export schedules to CSV format

## Customizable Parameters
- Minimum rest between shifts (8 hours by default)
- Worker-specific constraints
- Schedule preferences

## Advanced Features
- 12-hour schedule generation
- Automatic gap filling in the schedule
- Evaluation of night shift distribution
- Management of closely scheduled shifts



