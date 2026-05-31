import React, { useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { getCalendarColor } from "@/lib/calendarColors";

const DAYS_SHORT = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];


function sameDay(a, b) {
  return a.getFullYear()===b.getFullYear() && a.getMonth()===b.getMonth() && a.getDate()===b.getDate();
}

export default function MiniCalendar({ events = [], onDayClick }) {
  const today = new Date();
  const [cursor, setCursor] = useState(new Date(today.getFullYear(), today.getMonth(), 1));
  const year = cursor.getFullYear();
  const month = cursor.getMonth();
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const daysInPrev = new Date(year, month, 0).getDate();

  const eventDays = new Map();
  events.forEach(e => {
      const d = new Date(e.eventDate + "T00:00:00");
      const key = `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
      if (!eventDays.has(key)) eventDays.set(key, getCalendarColor(e.courseCode));
    });

  const cells = [];
  // trailing days from previous month
  for (let i = firstDay - 1; i >= 0; i--) {
    cells.push({ date: new Date(year, month - 1, daysInPrev - i), current: false });
  }
  // current month
  for (let d = 1; d <= daysInMonth; d++) {
    cells.push({ date: new Date(year, month, d), current: true });
  }
  // leading days from next month
  const remaining = 42 - cells.length;
  for (let d = 1; d <= remaining; d++) {
    cells.push({ date: new Date(year, month + 1, d), current: false });
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4">
      <p className="text-[13px] font-bold text-slate-800 mb-3">Calendar</p>

      {/* Month header */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-[11px] font-bold text-slate-700">
          Month {year}
        </span>
        <div className="flex gap-1">
          <button onClick={() => setCursor(new Date(year, month - 1, 1))}
            className="h-5 w-5 flex items-center justify-center rounded hover:bg-slate-100">
            <ChevronLeft size={11} className="text-slate-500"/>
          </button>
          <button onClick={() => setCursor(new Date(year, month + 1, 1))}
            className="h-5 w-5 flex items-center justify-center rounded hover:bg-slate-100">
            <ChevronRight size={11} className="text-slate-500"/>
          </button>
        </div>
      </div>

      {/* Day headers */}
      <div className="grid grid-cols-7 mb-1">
        {DAYS_SHORT.map(d => (
          <div key={d} className="text-center text-[9px] font-bold text-slate-400 py-0.5">{d}</div>
        ))}
      </div>

      {/* Day cells */}
      <div className="grid grid-cols-7 gap-y-0.5">
        {cells.map((cell, i) => {
          const key = `${cell.date.getFullYear()}-${cell.date.getMonth()}-${cell.date.getDate()}`;
          const isToday = sameDay(cell.date, today);
          const eventColor = eventDays.get(key);
          return (
            <button
              key={i}
              onClick={() => onDayClick?.(cell.date)}
              className={`relative flex h-6 w-full items-center justify-center rounded text-[10px] font-medium transition-colors
                ${!cell.current ? "text-slate-300" : "text-slate-700 hover:bg-slate-100"}
                ${isToday ? "!bg-indigo-600 !text-white rounded font-bold" : ""}
              `}
            >
              {cell.date.getDate()}
              {eventColor && !isToday && (
                <span className={`absolute bottom-0.5 left-1/2 h-1 w-1 -translate-x-1/2 rounded-full ${eventColor.dot}`}/>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

