import React, { useState, useEffect } from "react";
import {
  BookOpen, Plus, ChevronDown, ChevronRight, ArrowLeft,
  File, Presentation, Link2, FileEdit, Calendar as CalIcon,
  GraduationCap, User
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import Sidebar from "./Sidebar";
import ForumSection from "./Forumsection";
import SettingsPage from "./SettingsPage";
import { getCalendarColor } from "@/lib/calendarColors";
import {
  getStoredUser, getLecturerCourses, getCourseContent, getCourseMembers,
  createSection, createSectionItem, getAssignmentSubmissions, gradeSubmission, getCourseCalendarEvents,
  createCalendarEvent, createForum, getCourseForums
} from "@/api";

const itemIcons = {
  file: <File size={15} className="text-slate-500"/>,
  slide: <Presentation size={15} className="text-indigo-500"/>,
  link: <Link2 size={15} className="text-sky-500"/>,
  assignment: <FileEdit size={15} className="text-orange-500"/>,
};

// -- Course Manager (detail view for a lecturer's course) ---------------------
function CourseManager({ course, onBack }) {
  const courseCode = course.courseCode;
  const [tab, setTab] = useState("Content");
  const [content, setContent] = useState([]);
  const [openSecs, setOpenSecs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [members, setMembers] = useState([]);
  const [loadingMembers, setLoadingMembers] = useState(false);
  const [events, setEvents] = useState([]);
  const [loadingEvents, setLoadingEvents] = useState(false);

  // Add section form
  const [newSecName, setNewSecName] = useState("");
  const [addingSection, setAddingSection] = useState(false);
  const [sectionMsg, setSectionMsg] = useState(null);

  // Add item form
  const [activeSecID, setActiveSecID] = useState(null);
  const [itemForm, setItemForm] = useState({ title:"", secBody:"", secContent:"", itemtype:"file", dueDate:"" });
  const [addingItem, setAddingItem] = useState(false);
  const [itemMsg, setItemMsg] = useState(null);

  // Grade form
  const [gradeInputs, setGradeInputs] = useState({});
  const [gradingMsg, setGradingMsg] = useState(null);
  const [submissionsByItem, setSubmissionsByItem] = useState({});
  const [loadingSubmissions, setLoadingSubmissions] = useState({});

  // Calendar form
  const [calForm, setCalForm] = useState({ eventDate:"", eventTitle:"" });
  const [addingEvent, setAddingEvent] = useState(false);
  const [calMsg, setCalMsg] = useState(null);

  // Forum form
  const [forumName, setForumName] = useState("");

  const [forums, setForums] = useState([]);
  const [selectedForum, setSelectedForum] = useState(null);

  const loadContent = React.useCallback(() => {
    setLoading(true);
    getCourseContent(courseCode).then(d => {
      setContent(d); setOpenSecs(d.map(s => s.secID)); setLoading(false);
    }).catch(() => setLoading(false));
  }, [courseCode]);

  useEffect(() => { loadContent(); }, [loadContent]);

  useEffect(() => {
    if (tab !== "Members") return;
    setLoadingMembers(true);
    getCourseMembers(courseCode).then(d => { setMembers(d); setLoadingMembers(false); }).catch(()=>setLoadingMembers(false));
  }, [tab, courseCode]);

  useEffect(() => {
    if (tab !== "Calendar") return;
    setLoadingEvents(true);
    getCourseCalendarEvents(courseCode).then(d => { setEvents(Array.isArray(d)?d:[]); setLoadingEvents(false); }).catch(()=>setLoadingEvents(false));
  }, [tab, courseCode]);

  useEffect(() => {
    if (tab !== "Forums") return;
    getCourseForums(courseCode).then(d => setForums(Array.isArray(d)?d:[])).catch(()=>{});
  }, [tab, courseCode]);

  const handleAddSection = async (e) => {
    e.preventDefault();
    if (!newSecName.trim()) return;
    setAddingSection(true);
    const r = await createSection(courseCode, newSecName);
    if (r.status === 201) { setSectionMsg("Section added!"); setNewSecName(""); loadContent(); }
    else setSectionMsg(r.error || "Error");
    setAddingSection(false);
    setTimeout(() => setSectionMsg(null), 3000);
  };

  const handleAddItem = async (e) => {
    e.preventDefault();
    setAddingItem(true);
    const payload = { ...itemForm };
    if (payload.itemtype !== "assignment") delete payload.dueDate;
    if (!payload.dueDate) delete payload.dueDate;
    const r = await createSectionItem(activeSecID, payload);
    if (r.status === 201) { setItemMsg("Item added!"); setItemForm({title:"",secBody:"",secContent:"",itemtype:"file",dueDate:""}); setActiveSecID(null); loadContent(); }
    else setItemMsg(r.error || "Error");
    setAddingItem(false);
    setTimeout(() => setItemMsg(null), 3000);
  };

  const loadSubmissions = async (secItemID) => {
    setLoadingSubmissions(p => ({ ...p, [secItemID]: true }));
    try {
      const data = await getAssignmentSubmissions(secItemID);
      setSubmissionsByItem(p => ({ ...p, [secItemID]: Array.isArray(data) ? data : [] }));
    } catch {
      setSubmissionsByItem(p => ({ ...p, [secItemID]: [] }));
    } finally {
      setLoadingSubmissions(p => ({ ...p, [secItemID]: false }));
    }
  };

  const handleGrade = async (subID, secItemID) => {
    const g = parseInt(gradeInputs[subID]);
    if (isNaN(g) || g < 0 || g > 100) { setGradingMsg("Grade must be 0-100"); return; }
    const r = await gradeSubmission(subID, g);
    setGradingMsg(r.status === 200 ? "Graded!" : r.error || "Error");
    if (r.status === 200 && secItemID) loadSubmissions(secItemID);
    setTimeout(() => setGradingMsg(null), 3000);
  };

  const handleAddEvent = async (e) => {
    e.preventDefault();
    setAddingEvent(true);
    const r = await createCalendarEvent(courseCode, calForm);
    if (r.status === 201) { setCalMsg("Event created!"); setCalForm({eventDate:"",eventTitle:""}); setLoadingEvents(true); getCourseCalendarEvents(courseCode).then(d=>{setEvents(d);setLoadingEvents(false);}); }
    else setCalMsg(r.error || "Error");
    setAddingEvent(false);
    setTimeout(() => setCalMsg(null), 3000);
  };

  const handleAddForum = async (e) => {
    e.preventDefault();
    if (!forumName.trim()) return;
    const r = await createForum(courseCode, forumName);
    if (r.status === 201) { setForumName(""); getCourseForums(courseCode).then(d=>setForums(d)); }
  };

  const toggleSec = id => setOpenSecs(p => p.includes(id) ? p.filter(x=>x!==id) : [...p,id]);

  return (
    <div className="flex flex-col gap-5">
      <div>
        <Button variant="ghost" size="sm" onClick={onBack} className="gap-1 text-indigo-600 mb-2">
          <ArrowLeft size={14}/> Back
        </Button>
        <h1 className="text-[22px] font-extrabold text-slate-900">{course.courseCode}: {course.courseName}</h1>
        <div className="mt-3 flex gap-2 flex-wrap">
          {["Content","Members","Calendar","Forums"].map(t => (
            <button key={t} onClick={()=>setTab(t)}
              className={`rounded-full px-4 py-1.5 text-[12px] font-bold transition-colors ${tab===t?"bg-indigo-600 text-white":"text-slate-500 hover:text-slate-700"}`}>
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* -- CONTENT TAB -- */}
      {tab === "Content" && (
        <div className="flex flex-col gap-4">
          {/* Add section */}
          <div className="rounded-xl border border-slate-200 bg-white p-4">
            <p className="text-[13px] font-bold text-slate-700 mb-3">Add New Section</p>
            <form onSubmit={handleAddSection} className="flex gap-2">
              <Input placeholder="Section name..." value={newSecName} onChange={e=>setNewSecName(e.target.value)} className="h-9 text-[13px]" required/>
              <Button type="submit" size="sm" disabled={addingSection} className="h-9 bg-indigo-600 hover:bg-indigo-700 gap-1">
                <Plus size={13}/> Add
              </Button>
            </form>
            {sectionMsg && <p className="text-[11px] text-emerald-600 mt-2">{sectionMsg}</p>}
          </div>

          {loading ? <Skeleton className="h-20 w-full rounded-xl"/> :
            content.map(sec => {
              const open = openSecs.includes(sec.secID);
              return (
                <div key={sec.secID} className="rounded-xl border border-slate-200 bg-white overflow-hidden">
                  <button onClick={()=>toggleSec(sec.secID)}
                    className="flex w-full items-center justify-between px-4 py-3 text-left text-[14px] font-bold text-slate-800 hover:bg-slate-50">
                    <span className="flex items-center gap-2">
                      {open?<ChevronDown size={16}/>:<ChevronRight size={16}/>} {sec.secName}
                    </span>
                    <Button size="sm" variant="outline" className="h-7 gap-1 text-[11px]" onClick={e=>{e.stopPropagation();setActiveSecID(activeSecID===sec.secID?null:sec.secID);}}>
                      <Plus size={11}/> Add Item
                    </Button>
                  </button>

                  {activeSecID === sec.secID && (
                    <div className="border-t border-slate-100 bg-slate-50 px-4 py-3">
                      <form onSubmit={handleAddItem} className="flex flex-col gap-2">
                        <div className="grid grid-cols-2 gap-2">
                          <Input placeholder="Title *" value={itemForm.title} onChange={e=>setItemForm(p=>({...p,title:e.target.value}))} className="h-8 text-[12px]" required/>
                          <Select value={itemForm.itemtype} onValueChange={v=>setItemForm(p=>({...p,itemtype:v}))}>
                            <SelectTrigger className="h-8 text-[12px]"><SelectValue/></SelectTrigger>
                            <SelectContent>
                              <SelectItem value="file">File</SelectItem>
                              <SelectItem value="slide">Slide</SelectItem>
                              <SelectItem value="link">Link</SelectItem>
                              <SelectItem value="assignment">Assignment</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <Input placeholder="Description (optional)" value={itemForm.secBody} onChange={e=>setItemForm(p=>({...p,secBody:e.target.value}))} className="h-8 text-[12px]"/>
                        <Input placeholder="Content/URL (optional)" value={itemForm.secContent} onChange={e=>setItemForm(p=>({...p,secContent:e.target.value}))} className="h-8 text-[12px]"/>
                        {itemForm.itemtype==="assignment" && (
                          <Input type="date" value={itemForm.dueDate} onChange={e=>setItemForm(p=>({...p,dueDate:e.target.value}))} className="h-8 text-[12px]"/>
                        )}
                        <div className="flex gap-2">
                          <Button type="submit" size="sm" disabled={addingItem} className="h-8 bg-indigo-600 hover:bg-indigo-700 text-[11px]">Save Item</Button>
                          <Button type="button" size="sm" variant="ghost" className="h-8 text-[11px]" onClick={()=>setActiveSecID(null)}>Cancel</Button>
                        </div>
                        {itemMsg && <p className="text-[11px] text-emerald-600">{itemMsg}</p>}
                      </form>
                    </div>
                  )}

                  {open && <>
                    <Separator/>
                    {sec.items.length===0
                      ? <p className="px-4 py-3 text-[12px] italic text-slate-400">No items yet.</p>
                      : sec.items.map((item,i) => (
                        <React.Fragment key={item.secItemID}>
                          {i>0&&<Separator/>}
                          <div className="flex flex-col px-4 py-3 gap-2">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-3">
                                <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-slate-50">
                                  {itemIcons[item.itemtype]||<FileEdit size={15}/>}
                                </div>
                                <div>
                                  <p className="text-[13px] font-semibold text-slate-800">{item.title}</p>
                                  {item.secBody&&<p className="text-[11px] text-slate-400">{item.secBody}</p>}
                                </div>
                              </div>
                              {item.dueDate&&<Badge variant="destructive" className="text-[10px]">Due: {item.dueDate}</Badge>}
                            </div>
                            {item.itemtype==="assignment" && (
                              <div className="flex flex-col gap-2 pl-10">
                                <Button type="button" size="sm" variant="outline"
                                  disabled={loadingSubmissions[item.secItemID]}
                                  onClick={()=>loadSubmissions(item.secItemID)}
                                  className="h-8 w-fit text-[11px]">
                                  {loadingSubmissions[item.secItemID] ? "Loading..." : "View Submissions"}
                                </Button>
                                {(submissionsByItem[item.secItemID] || []).map(sub => (
                                  <div key={sub.subID} className="flex flex-wrap items-center gap-2 rounded-lg border border-slate-100 bg-slate-50 px-3 py-2">
                                    <div className="min-w-[180px] flex-1">
                                      <p className="text-[12px] font-semibold text-slate-700">{sub.fname} {sub.lname} <span className="text-slate-400">#{sub.subID}</span></p>
                                      <p className="text-[11px] text-slate-400">{sub.subText || sub.subContent || "No submission text"}</p>
                                    </div>
                                    <Input type="number" min="0" max="100" placeholder={sub.grade ?? "Grade"}
                                      value={gradeInputs[sub.subID] ?? ""}
                                      onChange={e=>setGradeInputs(p=>({...p,[sub.subID]:e.target.value}))}
                                      className="h-8 w-[110px] text-[12px]"/>
                                    <Button size="sm" className="h-8 text-[11px] bg-emerald-600 hover:bg-emerald-700"
                                      onClick={()=>handleGrade(sub.subID, item.secItemID)}>
                                      Save Grade
                                    </Button>
                                  </div>
                                ))}
                                {submissionsByItem[item.secItemID]?.length === 0 && (
                                  <p className="text-[11px] text-slate-400">No submissions yet.</p>
                                )}
                              </div>
                            )}
                          </div>
                        </React.Fragment>
                      ))
                    }
                  </>}
                </div>
              );
            })
          }
          {gradingMsg && <p className="text-[12px] font-semibold text-emerald-600">{gradingMsg}</p>}
        </div>
      )}

      {/* -- MEMBERS TAB -- */}
      {tab === "Members" && (
        <div className="flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <h2 className="text-[15px] font-extrabold text-slate-900">Class Roster</h2>
            <span className="text-[12px] text-slate-400">{members.length} members</span>
          </div>
          {loadingMembers ? <Skeleton className="h-32 w-full rounded-xl"/> :
            <div className="rounded-xl border border-slate-200 overflow-hidden">
              {members.map((p,i) => {
                const isL = p.memberRole?.toLowerCase()==="lecturer";
                return <React.Fragment key={p.userID}>
                  {i>0&&<Separator/>}
                  <div className="flex items-center justify-between px-4 py-3 bg-white">
                    <div className="flex items-center gap-3">
                      <div className={`flex h-8 w-8 items-center justify-center rounded-full ${isL?"bg-slate-100":"bg-indigo-100"}`}>
                        {isL?<GraduationCap size={15} className="text-slate-500"/>:<User size={15} className="text-indigo-500"/>}
                      </div>
                      <div>
                        <p className="text-[13px] font-bold text-slate-800">{p.fname} {p.lname}</p>
                        <p className="text-[11px] text-slate-400">{p.email}</p>
                      </div>
                    </div>
                    <Badge variant={isL?"secondary":"outline"} className="text-[10px] capitalize">{p.memberRole}</Badge>
                  </div>
                </React.Fragment>;
              })}
            </div>
          }
        </div>
      )}

      {/* -- CALENDAR TAB -- */}
      {tab === "Calendar" && (
        <div className="flex flex-col gap-4">
          <h2 className="text-[15px] font-extrabold text-slate-900">Course Calendar</h2>
          <div className="rounded-xl border border-slate-200 bg-white p-4">
            <p className="text-[13px] font-bold text-slate-700 mb-3">Create Event</p>
            <form onSubmit={handleAddEvent} className="flex flex-col gap-2">
              <Input placeholder="Event title *" value={calForm.eventTitle} onChange={e=>setCalForm(p=>({...p,eventTitle:e.target.value}))} className="h-9 text-[13px]" required/>
              <Input type="date" value={calForm.eventDate} onChange={e=>setCalForm(p=>({...p,eventDate:e.target.value}))} className="h-9 text-[13px]" required/>
              <Button type="submit" size="sm" disabled={addingEvent} className="h-9 w-fit bg-indigo-600 hover:bg-indigo-700">Add Event</Button>
            </form>
            {calMsg&&<p className="text-[11px] text-emerald-600 mt-2">{calMsg}</p>}
          </div>
          {loadingEvents ? <Skeleton className="h-20 w-full rounded-xl"/> :
            events.length===0 ? <p className="text-sm italic text-slate-400">No events yet.</p> :
            <div className="flex flex-col gap-2">
              {events.map(ev=>{
                const color = getCalendarColor(ev.courseCode || course.courseCode);
                return (
                <div key={ev.eventID} className={`flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 border-l-4 ${color.border}`}>
                  <div className={`flex h-9 w-9 items-center justify-center rounded-lg ${color.bg}`}><CalIcon size={16} className={color.text}/></div>
                  <div>
                    <p className="text-[13px] font-bold text-slate-800">{ev.eventTitle}</p>
                    <p className="text-[11px] text-slate-400">{ev.eventDate}</p>
                  </div>
                </div>
              );})}
            </div>
          }
        </div>
      )}

      {/* -- FORUMS TAB -- */}
      {tab === "Forums" && (
        selectedForum
          ? <ForumSection courseCode={course.courseCode}/>
          : <div className="flex flex-col gap-4">
              <h2 className="text-[15px] font-extrabold text-slate-900">Forums</h2>
              <div className="rounded-xl border border-slate-200 bg-white p-4">
                <p className="text-[13px] font-bold text-slate-700 mb-3">Create Forum</p>
                <form onSubmit={handleAddForum} className="flex gap-2">
                  <Input placeholder="Forum name *" value={forumName} onChange={e=>setForumName(e.target.value)} className="h-9 text-[13px]" required/>
                  <Button type="submit" size="sm" className="h-9 bg-indigo-600 hover:bg-indigo-700 gap-1"><Plus size={13}/>Add</Button>
                </form>
              </div>
              <div className="flex flex-col gap-2">
                {forums.map(f=>(
                  <button key={f.dfID} onClick={()=>setSelectedForum(f)}
                    className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 text-left hover:border-indigo-300 hover:bg-indigo-50">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-100">
                      <BookOpen size={16} className="text-indigo-600"/>
                    </div>
                    <span className="text-[13px] font-bold text-slate-800">{f.dfname}</span>
                  </button>
                ))}
              </div>
            </div>
      )}
    </div>
  );
}

// -- Main Lecturer Dashboard ---------------------------------------------------
export default function LecturerDashboard() {
  const [activeTab, setActiveTab] = useState("My Courses");
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const user = getStoredUser();
  const userID = user?.userID;

  useEffect(() => {
    if (!userID) return;
    getLecturerCourses(userID)
      .then(d => { setCourses(Array.isArray(d)?d:[]); setLoading(false); })
      .catch(() => setLoading(false));
  }, [userID]);

  const renderContent = () => {
    if (activeTab === "My Courses" && selectedCourse)
      return <CourseManager course={selectedCourse} onBack={() => setSelectedCourse(null)} />;

    switch (activeTab) {
      case "My Courses":
        return (
          <div className="flex flex-col gap-5">
            <div>
              <h1 className="text-[24px] font-extrabold text-slate-900">My Courses</h1>
              <p className="text-[13px] text-slate-400 mt-0.5">{courses.length} assigned course{courses.length!==1?"s":""}</p>
            </div>
            {loading
              ? <div className="flex flex-col gap-3">{[1,2].map(i=><Skeleton key={i} className="h-24 rounded-xl"/>)}</div>
              : courses.length===0
              ? <p className="text-sm italic text-slate-400">No courses assigned yet.</p>
              : <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                  {courses.map(c=>(
                    <div key={c.courseCode} onClick={()=>setSelectedCourse(c)}
                      className="flex h-[90px] cursor-pointer items-center overflow-hidden rounded-xl border border-slate-100 bg-white shadow-sm hover:border-indigo-300 hover:bg-indigo-50 transition-all">
                      <div className="h-full w-[80px] shrink-0 bg-indigo-100 flex items-center justify-center">
                        <BookOpen size={22} className="text-indigo-400"/>
                      </div>
                      <div className="flex flex-col justify-center px-4">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">{c.courseCode}</span>
                        <span className="text-[13px] font-bold text-slate-900 leading-tight">{c.courseName}</span>
                        <span className="text-[10px] text-slate-400">{c.department}</span>
                      </div>
                    </div>
                  ))}
                </div>
            }
          </div>
        );

      case "Calendar":
        return (
          <div className="flex flex-col gap-4">
            <h1 className="text-[24px] font-extrabold text-slate-900">Teaching Calendar</h1>
            <p className="text-[13px] text-slate-400">Select a course to manage its calendar events.</p>
            <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
              {courses.map(c=>(
                <button key={c.courseCode} onClick={()=>{setSelectedCourse(c);setActiveTab("My Courses");}}
                  className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 text-left hover:border-indigo-300">
                  <CalIcon size={16} className="text-indigo-400"/>
                  <span className="text-[13px] font-bold text-slate-800">{c.courseCode}: {c.courseName}</span>
                </button>
              ))}
            </div>
          </div>
        );

      case "Settings":
        return <SettingsPage/>;

      default:
        return null;
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar activeTab={activeTab} setActiveTab={t=>{setActiveTab(t);setSelectedCourse(null);}}/>
      <div className="flex flex-1 flex-col gap-6 overflow-y-auto p-8 box-border">{renderContent()}</div>
    </div>
  );
}




