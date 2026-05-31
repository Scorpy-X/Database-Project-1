import React, { useState, useEffect } from "react";
import { ChevronLeft, ChevronRight, Plus, Check } from "lucide-react";

import { getStoredUser, getStudentCalendarEvents, getStudentCourses } from "@/api";
import { getCalendarColor } from "@/lib/calendarColors";

const DAYS_FULL  = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
const DAYS_SHORT = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
const MONTHS     = ["January","February","March","April","May","June","July","August","September","October","November","December"];
const HOURS      = Array.from({ length: 13 }, (_, i) => i + 8); // 8am â€“ 8pm

function sameDay(a, b) {
  return a.getFullYear()===b.getFullYear() && a.getMonth()===b.getMonth() && a.getDate()===b.getDate();
}
function weekStart(date) {
  const d = new Date(date);
  d.setDate(d.getDate() - d.getDay());
  d.setHours(0,0,0,0);
  return d;
}

// â”€â”€ Left sidebar mini-calendar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function SidebarMiniCal({ cursor, onNav, onDayClick, events }) {
  const today = new Date();
  const year  = cursor.getFullYear();
  const month = cursor.getMonth();
  const firstDay     = new Date(year, month, 1).getDay();
  const daysInMonth  = new Date(year, month+1, 0).getDate();
  const daysInPrev   = new Date(year, month,   0).getDate();

  const eventDays = new Map();
  events.forEach(e => {
    const d = new Date(e.eventDate + "T00:00:00");
    const key = `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
    if (!eventDays.has(key)) eventDays.set(key, getCalendarColor(e.courseCode));
  });

  const cells = [];
  for (let i = firstDay-1; i >= 0; i--)
    cells.push({ date: new Date(year, month-1, daysInPrev-i), cur: false });
  for (let d = 1; d <= daysInMonth; d++)
    cells.push({ date: new Date(year, month, d), cur: true });
  while (cells.length < 35)
    cells.push({ date: new Date(year, month+1, cells.length-daysInMonth-firstDay+1), cur: false });

  return (
    <div className="w-[160px] shrink-0">
      {/* Month navigation */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-[11px] font-bold text-slate-700">Month {year}</span>
        <div className="flex gap-0.5">
          <button onClick={() => onNav(-1)} className="h-5 w-5 flex items-center justify-center rounded hover:bg-slate-200">
            <ChevronLeft size={11} className="text-slate-500"/>
          </button>
          <button onClick={() => onNav(1)} className="h-5 w-5 flex items-center justify-center rounded hover:bg-slate-200">
            <ChevronRight size={11} className="text-slate-500"/>
          </button>
        </div>
      </div>

      {/* Day headers */}
      <div className="grid grid-cols-7">
        {DAYS_SHORT.map(d => (
          <div key={d} className="text-center text-[9px] font-semibold text-slate-400 pb-1">{d}</div>
        ))}
      </div>

      {/* Day cells */}
      <div className="grid grid-cols-7 gap-y-0.5">
        {cells.map((cell, i) => {
          const key = `${cell.date.getFullYear()}-${cell.date.getMonth()}-${cell.date.getDate()}`;
          const isToday = sameDay(cell.date, today);
          const eventColor = eventDays.get(key);
          return (
            <button key={i} onClick={() => onDayClick(cell.date)}
              className={`relative flex h-[22px] w-full items-center justify-center rounded text-[9px] font-medium transition-colors
                ${!cell.cur ? "text-slate-300" : "text-slate-600 hover:bg-slate-100"}
                ${isToday ? "!bg-indigo-600 !text-white font-bold" : ""}
              `}>
              {cell.date.getDate()}
              {eventColor && !isToday && (
                <span className={`absolute bottom-0 left-1/2 h-[3px] w-[3px] -translate-x-1/2 rounded-full ${eventColor.dot}`}/>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

// â”€â”€ My Calendars list â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function MyCalendars({ courses, enabled, onToggle }) {
  return (
    <div className="mt-5">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[12px] font-extrabold text-slate-800">My Calendars</span>
        <button className="h-5 w-5 flex items-center justify-center rounded-full hover:bg-slate-200">
          <Plus size={12} className="text-slate-500"/>
        </button>
      </div>
      <div className="flex flex-col gap-1.5">
        {courses.map((c) => {
          const color = getCalendarColor(c.courseCode);
          const on = enabled.has(c.courseCode);
          return (
            <button key={c.courseCode} onClick={() => onToggle(c.courseCode)}
              className="flex items-center gap-2 text-left">
              <div className={`flex h-4 w-4 shrink-0 items-center justify-center rounded ${on ? color.dot : "bg-slate-200"}`}>
                {on && <Check size={9} color="#fff" strokeWidth={3}/>}
              </div>
              <span className="text-[11px] text-slate-700 truncate max-w-[110px]">{c.courseName || c.courseCode}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

// â”€â”€ MONTH VIEW â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function MonthView({ cursor, events, enabled, onDayClick }) {
  const year     = cursor.getFullYear();
  const month    = cursor.getMonth();
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month+1, 0).getDate();
  const daysInPrev  = new Date(year, month, 0).getDate();
  const today    = new Date();

  const cells = [];
  for (let i = firstDay-1; i >= 0; i--)
    cells.push({ date: new Date(year, month-1, daysInPrev-i), cur: false });
  for (let d = 1; d <= daysInMonth; d++)
    cells.push({ date: new Date(year, month, d), cur: true });
  while (cells.length < 35)
    cells.push({ date: new Date(year, month+1, cells.length-daysInMonth-firstDay+1), cur: false });

  const eventsOnDay = (date) =>
    events.filter(e => {
      if (!enabled.has(e.courseCode)) return false;
      return sameDay(new Date(e.eventDate + "T00:00:00"), date);
    });

  return (
    <div className="flex flex-col flex-1 overflow-hidden">
      {/* Day name headers */}
      <div className="grid grid-cols-7 border-b border-slate-200 bg-white">
        {DAYS_FULL.map(d => (
          <div key={d} className="py-2 text-center text-[11px] font-semibold text-slate-500">{d}</div>
        ))}
      </div>

      {/* Grid */}
      <div className="grid grid-cols-7 flex-1" style={{ gridTemplateRows: `repeat(${cells.length/7}, 1fr)` }}>
        {cells.map((cell, i) => {
          const isToday = sameDay(cell.date, today);
          const dayEvents = eventsOnDay(cell.date);
          return (
            <div key={i} onClick={() => onDayClick(cell.date)}
              className={`border-b border-r border-slate-200 min-h-[90px] p-1 cursor-pointer hover:bg-slate-50 transition-colors
                ${!cell.cur ? "bg-slate-50/50" : "bg-white"}
              `}>
              <div className="flex items-center justify-end mb-1">
                <span className={`flex h-6 w-6 items-center justify-center rounded-full text-[11px] font-semibold
                  ${isToday ? "bg-indigo-600 text-white" : !cell.cur ? "text-slate-300" : "text-slate-600"}
                `}>
                  {cell.date.getDate()}
                </span>
              </div>
              <div className="flex flex-col gap-0.5">
                {dayEvents.slice(0,2).map((ev, j) => {
                  const col = getCalendarColor(ev.courseCode);
                  return (
                    <div key={j} className={`flex items-center gap-1 rounded px-1 py-0.5 ${col.bg}`}>
                      <div className={`h-1.5 w-1.5 shrink-0 rounded-full ${col.dot}`}/>
                      <span className={`text-[9px] font-semibold truncate ${col.text}`}>{ev.eventTitle}</span>
                    </div>
                  );
                })}
                {dayEvents.length > 2 && (
                  <span className="text-[9px] text-slate-400 pl-1">+{dayEvents.length-2} more</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// â”€â”€ WEEK VIEW â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function WeekView({ cursor, events, enabled }) {
  const ws = weekStart(cursor);
  const days = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(ws); d.setDate(ws.getDate() + i); return d;
  });
  const today = new Date();
  const eventsOnDay = (date) =>
    events.filter(e => enabled.has(e.courseCode) && sameDay(new Date(e.eventDate + "T00:00:00"), date));

  return (
    <div className="flex flex-col flex-1 overflow-hidden">
      {/* Day headers */}
      <div className="grid border-b border-slate-200 bg-white" style={{ gridTemplateColumns:"56px repeat(7,1fr)" }}>
        <div className="border-r border-slate-200"/>
        {days.map((d, i) => {
          const isToday = sameDay(d, today);
          return (
            <div key={i} className={`py-2 text-center border-r border-slate-200 ${isToday ? "bg-indigo-50" : ""}`}>
              <p className="text-[10px] font-semibold text-slate-400">{DAYS_SHORT[d.getDay()]}</p>
              <div className={`mx-auto mt-0.5 flex h-7 w-7 items-center justify-center rounded-full text-[13px] font-bold
                ${isToday ? "bg-indigo-600 text-white" : "text-slate-700"}
              `}>
                {d.getDate()}
              </div>
            </div>
          );
        })}
      </div>

      {/* Time grid */}
      <div className="flex-1 overflow-y-auto">
        {HOURS.map(h => (
          <div key={h} className="grid border-b border-slate-100" style={{ gridTemplateColumns:"56px repeat(7,1fr)", minHeight:"52px" }}>
            {/* Time label */}
            <div className="border-r border-slate-200 pr-2 pt-0">
              <span className="text-[10px] text-slate-400 font-medium flex justify-end -mt-2">
                {h === 12 ? "12 PM" : h > 12 ? `${h-12} PM` : `${h} AM`}
              </span>
            </div>
            {days.map((d, i) => {
              const isToday = sameDay(d, today);
              const dayEvents = eventsOnDay(d);
              return (
                <div key={i} className={`border-r border-slate-100 relative px-0.5 pt-0.5
                  ${isToday ? "bg-indigo-50/30" : ""}
                `}>
                  {dayEvents.map((ev, j) => {
                    const col = getCalendarColor(ev.courseCode);
                    return (
                      <div key={j} className={`mb-0.5 rounded px-1 py-0.5 ${col.bg} border-l-2 ${col.border}`}>
                        <p className={`text-[9px] font-bold truncate ${col.text}`}>{ev.eventTitle}</p>
                      </div>
                    );
                  })}
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
}

// â”€â”€ DAY VIEW â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function DayView({ cursor, events, enabled }) {
  const today = new Date();
  const dayEvents = events.filter(e =>
    enabled.has(e.courseCode) && sameDay(new Date(e.eventDate + "T00:00:00"), cursor)
  );

  return (
    <div className="flex flex-col flex-1 overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-3 border-b border-slate-200 px-6 py-3 bg-white">
        <div className={`flex h-10 w-10 items-center justify-center rounded-full text-[16px] font-extrabold
          ${sameDay(cursor, today) ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-700"}
        `}>
          {cursor.getDate()}
        </div>
        <div>
          <p className="text-[14px] font-extrabold text-slate-900">{DAYS_FULL[cursor.getDay()]}</p>
          <p className="text-[11px] text-slate-400">{MONTHS[cursor.getMonth()]} {cursor.getFullYear()}</p>
        </div>
      </div>

      {/* Time slots */}
      <div className="flex-1 overflow-y-auto">
        {HOURS.map(h => {
          const hEvents = dayEvents; // all events show in day view
          return (
            <div key={h} className="flex gap-0 border-b border-slate-100 min-h-[52px]">
              <div className="w-[56px] shrink-0 pr-3 -mt-2">
                <span className="text-[10px] text-slate-400 flex justify-end">
                  {h === 12 ? "12 PM" : h > 12 ? `${h-12} PM` : `${h} AM`}
                </span>
              </div>
              <div className="flex-1 border-l border-slate-200 px-2 pt-0.5">
                {h === 9 && hEvents.map((ev, j) => {
                  const col = getCalendarColor(ev.courseCode);
                  return (
                    <div key={j} className={`mb-1 rounded-lg px-3 py-2 ${col.bg} border-l-4 ${col.border}`}>
                      <p className={`text-[12px] font-bold ${col.text}`}>{ev.eventTitle}</p>
                      {ev.courseName && <p className={`text-[10px] ${col.text} opacity-70`}>{ev.courseName}</p>}
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// â”€â”€ MAIN CALENDAR PAGE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
export default function CalendarPage() {
  const user    = getStoredUser();
  const today   = new Date();

  const [viewMode, setViewMode]   = useState("Month"); // Day | Week | Month
  const [cursor, setCursor]       = useState(new Date(today.getFullYear(), today.getMonth(), 1));
  const [events, setEvents]       = useState([]);
  const [courses, setCourses]     = useState([]);
  const [enabled, setEnabled]     = useState(new Set());
  const [loading, setLoading]     = useState(true);

  useEffect(() => {
    if (!user) return;
    Promise.all([
      getStudentCalendarEvents(user.userID).catch(() => []),
      getStudentCourses(user.userID).catch(() => []),
    ]).then(([evts, crs]) => {
      const evArr  = Array.isArray(evts) ? evts : [];
      const crArr  = Array.isArray(crs)  ? crs  : [];
      setEvents(evArr);
      setCourses(crArr);
      setEnabled(new Set(crArr.map(c => c.courseCode)));
      setLoading(false);
    });
  }, [user?.userID]);

  const toggleCourse = (code) => {
    setEnabled(prev => {
      const next = new Set(prev);
      next.has(code) ? next.delete(code) : next.add(code);
      return next;
    });
  };

  const navigate = (dir) => {
    if (viewMode === "Month") {
      setCursor(new Date(cursor.getFullYear(), cursor.getMonth() + dir, 1));
    } else if (viewMode === "Week") {
      const d = new Date(cursor);
      d.setDate(d.getDate() + dir * 7);
      setCursor(d);
    } else {
      const d = new Date(cursor);
      d.setDate(d.getDate() + dir);
      setCursor(d);
    }
  };

  const headerLabel = () => {
    if (viewMode === "Month") return `${MONTHS[cursor.getMonth()]} ${cursor.getFullYear()}`;
    if (viewMode === "Week") {
      const ws = weekStart(cursor);
      const we = new Date(ws); we.setDate(ws.getDate() + 6);
      return `${MONTHS[ws.getMonth()]} ${ws.getFullYear()}`;
    }
    return `${DAYS_FULL[cursor.getDay()]}, ${MONTHS[cursor.getMonth()]} ${cursor.getDate()}`;
  };

  return (
    <div className="flex h-full min-h-screen bg-white font-sans">

      {/* â”€â”€ Left sidebar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      <div className="flex w-[192px] shrink-0 flex-col gap-4 border-r border-slate-200 bg-white px-4 py-5">
        {/* New Event button */}
        <button className="flex items-center gap-2 rounded-full bg-indigo-600 px-4 py-2 text-[12px] font-bold text-white shadow hover:bg-indigo-700 transition-colors">
          <Plus size={13}/> New Event +
        </button>

        {/* Mini calendar */}
        <SidebarMiniCal
          cursor={cursor}
          onNav={(dir) => setCursor(new Date(cursor.getFullYear(), cursor.getMonth() + dir, 1))}
          onDayClick={(d) => { setCursor(d); setViewMode("Day"); }}
          events={events}
        />

        {/* My Calendars */}
        <MyCalendars courses={courses} enabled={enabled} onToggle={toggleCourse}/>
      </div>

      {/* â”€â”€ Main area â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      <div className="flex flex-1 flex-col overflow-hidden">

        {/* Top bar */}
        <div className="flex items-center gap-3 border-b border-slate-200 bg-white px-5 py-3">
          {/* Arrow nav */}
          <div className="flex gap-1">
            <button onClick={() => navigate(-1)}
              className="flex h-7 w-7 items-center justify-center rounded-full hover:bg-slate-100 transition-colors">
              <ChevronLeft size={14} className="text-slate-600"/>
            </button>
            <button onClick={() => navigate(1)}
              className="flex h-7 w-7 items-center justify-center rounded-full hover:bg-slate-100 transition-colors">
              <ChevronRight size={14} className="text-slate-600"/>
            </button>
          </div>

          {/* Month label */}
          <h2 className="text-[16px] font-extrabold text-slate-900 flex-1">{headerLabel()}</h2>

          {/* Today */}
          <button onClick={() => setCursor(new Date())}
            className="rounded-lg border border-slate-300 px-3 py-1 text-[12px] font-semibold text-slate-600 hover:bg-slate-50 transition-colors">
            Today
          </button>

          {/* View switcher */}
          <div className="flex rounded-lg border border-slate-200 overflow-hidden">
            {["Day","Week","Month"].map(m => (
              <button key={m} onClick={() => setViewMode(m)}
                className={`px-3 py-1 text-[12px] font-semibold transition-colors
                  ${viewMode===m ? "bg-indigo-600 text-white" : "bg-white text-slate-500 hover:bg-slate-50"}
                `}>
                {m}
              </button>
            ))}
          </div>
        </div>

        {/* Calendar body */}
        {loading
          ? <div className="flex flex-1 items-center justify-center text-[13px] italic text-slate-400">Loading eventsâ€¦</div>
          : viewMode === "Month"
          ? <MonthView  cursor={cursor} events={events} courses={courses} enabled={enabled} onDayClick={d => { setCursor(d); setViewMode("Day"); }}/>
          : viewMode === "Week"
          ? <WeekView   cursor={cursor} events={events} courses={courses} enabled={enabled}/>
          : <DayView    cursor={cursor} events={events} courses={courses} enabled={enabled}/>
        }
      </div>
    </div>
  );
}







