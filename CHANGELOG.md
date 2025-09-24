# Changelog

All notable changes to this project will be documented in this file.

## [1.2.0] - 2024-12-19

### Added
- Results sidebar layout (moved from bottom panel)
- Resizable interface panels with horizontal splitter
- Improved UI layout for better space utilization

### Changed
- Results area moved from bottom to right sidebar
- Weekly column background now matches other table cells
- Enhanced visual consistency across the interface

### Fixed
- Weekly column background color in different themes
- Layout proportions for better user experience

## [1.1.0] - 2024-12-18

### Added
- Dark/Light theme toggle functionality
- Individual day counters with +/- buttons
- Save/Open project functionality (JSON format)
- Keyboard shortcuts (Ctrl+Enter for calculate, Ctrl+S for save)
- Progress bar and status indicators
- Tooltips for better user guidance
- Recent files menu
- Preferences dialog
- SQLite database for data persistence

### Changed
- Improved Excel parsing with better error handling
- Enhanced lab class detection (keywords: lab, practical, -P suffix)
- Better day-specific calculation logic
- Upgraded UI with modern styling

### Fixed
- Excel file format compatibility issues
- Lab class counting accuracy
- Theme switching consistency

## [1.0.0] - 2024-12-17

### Added
- Initial release
- Excel timetable import functionality
- Day-specific class calculation
- Holiday management with visual calendar
- Manual subject management
- Export results to text files
- Basic PyQt6 GUI interface

### Features
- Upload Excel files with days as rows, time slots as columns
- Calculate extra classes based on remaining weekdays
- Visual holiday selection
- Real-time calculation updates
- Export functionality