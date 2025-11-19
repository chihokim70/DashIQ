import { useState } from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Button } from "./ui/button";
import { Search } from "lucide-react";

interface FilterBarProps {
  onFilterChange?: (filters: { year: string; month: string; week: string }) => void;
}

export function FilterBar({ onFilterChange }: FilterBarProps) {
  const currentYear = 2025;
  const currentMonth = "11"; // November (현재 월)
  const currentWeek = "all"; // 전체 주 (This Month를 표현하기 위해 ALL로 설정)
  
  const [selectedYear, setSelectedYear] = useState(currentYear.toString());
  const [selectedMonth, setSelectedMonth] = useState(currentMonth);
  const [selectedWeek, setSelectedWeek] = useState(currentWeek);
  
  const years = Array.from({ length: 5 }, (_, i) => currentYear - i); // 2025, 2024, 2023, 2022, 2021
  const months = [
    { value: "all", label: "ALL" },
    { value: "01", label: "Jan" },
    { value: "02", label: "Feb" },
    { value: "03", label: "Mar" },
    { value: "04", label: "Apr" },
    { value: "05", label: "May" },
    { value: "06", label: "Jun" },
    { value: "07", label: "Jul" },
    { value: "08", label: "Aug" },
    { value: "09", label: "Sep" },
    { value: "10", label: "Oct" },
    { value: "11", label: "Nov" },
    { value: "12", label: "Dec" },
  ];
  const weeks = [
    { value: "all", label: "ALL" },
    { value: "1", label: "Week 1" },
    { value: "2", label: "Week 2" },
    { value: "3", label: "Week 3" },
    { value: "4", label: "Week 4" },
    { value: "5", label: "Week 5" },
  ];

  const handleSearch = () => {
    if (onFilterChange) {
      onFilterChange({
        year: selectedYear,
        month: selectedMonth,
        week: selectedWeek
      });
    }
  };

  const handleYearChange = (value: string) => {
    setSelectedYear(value);
  };

  const handleMonthChange = (value: string) => {
    setSelectedMonth(value);
  };

  const handleWeekChange = (value: string) => {
    setSelectedWeek(value);
  };

  return (
    <div className="flex flex-wrap items-center gap-3 mb-6">
      <Select value={selectedYear} onValueChange={handleYearChange}>
        <SelectTrigger className="w-[110px] bg-input-background border-border">
          <SelectValue placeholder="Year" />
        </SelectTrigger>
        <SelectContent>
          {years.map((year) => (
            <SelectItem key={year} value={year.toString()}>
              {year}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select value={selectedMonth} onValueChange={handleMonthChange}>
        <SelectTrigger className="w-[110px] bg-input-background border-border">
          <SelectValue placeholder="Month" />
        </SelectTrigger>
        <SelectContent>
          {months.map((month) => (
            <SelectItem key={month.value} value={month.value}>
              {month.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select value={selectedWeek} onValueChange={handleWeekChange}>
        <SelectTrigger className="w-[110px] bg-input-background border-border">
          <SelectValue placeholder="Week" />
        </SelectTrigger>
        <SelectContent>
          {weeks.map((week) => (
            <SelectItem key={week.value} value={week.value}>
              {week.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Button 
        className="bg-[#1E90FF] hover:bg-[#1E90FF]/90 text-white gap-2"
        size="default"
        onClick={handleSearch}
      >
        <Search className="w-4 h-4" />
        <span className="hidden sm:inline">Search</span>
      </Button>
    </div>
  );
}