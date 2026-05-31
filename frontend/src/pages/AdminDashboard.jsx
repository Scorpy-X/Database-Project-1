import React, { useState, useEffect } from "react";
import {
  Plus, Trash2, Users, BookOpen, AlertTriangle,
  GraduationCap, TrendingUp, RefreshCw, Search, UserPlus, ArrowLeft
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import Sidebar from "./Sidebar";
import SettingsPage from "./SettingsPage";
import {
  getCourses, createCourse, deleteCourse, enrollStudent,
  getUsers, registerUser, getStoredUser, getStoredPassword,
  getCourseMembers,
  reportCourses50, reportStudents5plus, reportLecturers3,
  reportMostEnrolled, reportTopStudents
} from "@/api";

// â”€â”€ Stat Card â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function StatCard({ icon: Icon, label, value, color = "bg-indigo-100", textColor = "text-indigo-600" }) {
  return (
    <div className="flex items-center gap-4 rounded-xl border border-slate-200 bg-white px-5 py-4">
      <div className={`flex h-11 w-11 items-center justify-center rounded-xl ${color}`}>
        <Icon size={20} className={textColor}/>
      </div>
      <div>
        <p className="text-[12px] text-slate-400 font-semibold">{label}</p>
        <p className="text-[22px] font-extrabold text-slate-900">{value ?? "â€”"}</p>
      </div>
    </div>
  );
}

// â”€â”€ Report Table â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function ReportTable({ title, columns, rows, loading }) {
  return (
    <div className="flex flex-col gap-2">
      <h3 className="text-[14px] font-extrabold text-slate-800">{title}</h3>
      {loading
        ? <Skeleton className="h-32 w-full rounded-xl"/>
        : rows.length === 0
        ? <p className="text-[12px] italic text-slate-400">No data.</p>
        : <div className="rounded-xl border border-slate-200 overflow-hidden">
            <div className="grid bg-slate-50 px-4 py-2 border-b border-slate-200" style={{gridTemplateColumns:`repeat(${columns.length},1fr)`}}>
              {columns.map(c=><span key={c.key} className="text-[10px] font-bold uppercase tracking-wider text-slate-500">{c.label}</span>)}
            </div>
            {rows.map((row,i)=>(
              <React.Fragment key={i}>
                {i>0&&<Separator/>}
                <div className="grid px-4 py-2.5 bg-white" style={{gridTemplateColumns:`repeat(${columns.length},1fr)`}}>
                  {columns.map(c=>(
                    <span key={c.key} className="text-[12px] text-slate-700 font-medium">{row[c.key] ?? "â€”"}</span>
                  ))}
                </div>
              </React.Fragment>
            ))}
          </div>
      }
    </div>
  );
}

// â”€â”€ Main Admin Dashboard â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function CourseRosterPanel({ course, members, loading, error, onBack }) {
  const lecturers = members.filter(m => m.memberRole?.toLowerCase() === "lecturer");
  const students = members.filter(m => m.memberRole?.toLowerCase() === "student");
  const lecturer = lecturers[0];

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      <div className="mb-4 flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <Button variant="ghost" size="sm" onClick={onBack} className="mb-2 h-8 gap-1 px-0 text-[12px] text-indigo-600 hover:bg-transparent">
            <ArrowLeft size={13}/> Back to courses
          </Button>
          <h2 className="text-[17px] font-extrabold text-slate-900">{course.courseCode}: {course.courseName}</h2>
          <p className="mt-1 text-[12px] text-slate-400">{course.department || "Department not listed"}</p>
        </div>
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="rounded-lg bg-slate-50 px-3 py-2">
            <p className="text-[16px] font-extrabold text-slate-900">{members.length}</p>
            <p className="text-[10px] font-semibold uppercase text-slate-400">Members</p>
          </div>
          <div className="rounded-lg bg-indigo-50 px-3 py-2">
            <p className="text-[16px] font-extrabold text-indigo-700">{students.length}</p>
            <p className="text-[10px] font-semibold uppercase text-indigo-400">Students</p>
          </div>
          <div className="rounded-lg bg-slate-50 px-3 py-2">
            <p className="text-[16px] font-extrabold text-slate-700">{lecturers.length}</p>
            <p className="text-[10px] font-semibold uppercase text-slate-400">Lecturers</p>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex flex-col gap-2">{[1,2,3].map(i => <Skeleton key={i} className="h-12 rounded-lg"/>)}</div>
      ) : error ? (
        <p className="rounded-lg border border-red-100 bg-red-50 px-3 py-2 text-[12px] font-semibold text-red-600">{error}</p>
      ) : (
        <div className="flex flex-col gap-4">
          <div className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3">
            <p className="text-[11px] font-bold uppercase text-slate-400">Assigned Lecturer</p>
            {lecturer ? (
              <p className="mt-1 text-[13px] font-bold text-slate-800">{lecturer.fname} {lecturer.lname} <span className="font-medium text-slate-400">({lecturer.email})</span></p>
            ) : (
              <p className="mt-1 text-[12px] italic text-slate-400">No lecturer returned for this course.</p>
            )}
          </div>

          <div>
            <div className="mb-2 flex items-center justify-between">
              <h3 className="text-[14px] font-extrabold text-slate-800">Enrolled Students</h3>
              <span className="text-[12px] text-slate-400">{students.length} student{students.length === 1 ? "" : "s"}</span>
            </div>
            {students.length === 0 ? (
              <p className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-[12px] italic text-slate-400">No enrolled students.</p>
            ) : (
              <div className="overflow-hidden rounded-lg border border-slate-200">
                {students.map((student, i) => (
                  <React.Fragment key={student.userID}>
                    {i > 0 && <Separator/>}
                    <div className="flex items-center justify-between bg-white px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-50">
                          <Users size={14} className="text-indigo-500"/>
                        </div>
                        <div>
                          <p className="text-[13px] font-bold text-slate-800">{student.fname} {student.lname}</p>
                          <p className="text-[11px] text-slate-400">{student.email}</p>
                        </div>
                      </div>
                      <Badge variant="outline" className="text-[10px]">ID {student.userID}</Badge>
                    </div>
                  </React.Fragment>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState("Dashboard");
  const user = getStoredUser();
  const password = getStoredPassword();

  // â”€â”€ Courses state â”€â”€
  const [courses, setCourses] = useState([]);
  const [loadingCourses, setLoadingCourses] = useState(true);
  const [courseSearch, setCourseSearch] = useState("");
  const [createForm, setCreateForm] = useState({ courseCode:"", courseName:"", department:"", lecturerID:"" });
  const [creating, setCreating] = useState(false);
  const [createMsg, setCreateMsg] = useState(null);
  const [deleteMsg, setDeleteMsg] = useState(null);
  const [enrollForm, setEnrollForm] = useState({ courseCode:"", userID:"" });
  const [enrollMsg, setEnrollMsg] = useState(null);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [courseMembers, setCourseMembers] = useState([]);
  const [loadingMembers, setLoadingMembers] = useState(false);
  const [membersError, setMembersError] = useState(null);

  // â”€â”€ Users state â”€â”€
  const [users, setUsers] = useState([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [userSearch, setUserSearch] = useState("");
  const [regForm, setRegForm] = useState({ fname:"", lname:"", email:"", accessLvl:"student" });
  const [registering, setRegistering] = useState(false);
  const [regMsg, setRegMsg] = useState(null);
  const [regResult, setRegResult] = useState(null);

  // â”€â”€ Reports state â”€â”€
  const [reports, setReports] = useState({ c50:[], s5plus:[], l3:[], enrolled:[], top:[] });
  const [loadingReports, setLoadingReports] = useState(false);

  const loadCourses = () => {
    setLoadingCourses(true);
    getCourses().then(d=>{setCourses(Array.isArray(d)?d:[]);setLoadingCourses(false);}).catch(()=>setLoadingCourses(false));
  };

  const loadUsers = () => {
    setLoadingUsers(true);
    getUsers().then(d=>{setUsers(Array.isArray(d)?d:[]);setLoadingUsers(false);}).catch(()=>setLoadingUsers(false));
  };

  const loadReports = async () => {
    setLoadingReports(true);
    const [c50, s5plus, l3, enrolled, top] = await Promise.all([
      reportCourses50().catch(()=>[]),
      reportStudents5plus().catch(()=>[]),
      reportLecturers3().catch(()=>[]),
      reportMostEnrolled().catch(()=>[]),
      reportTopStudents().catch(()=>[]),
    ]);
    setReports({ c50, s5plus, l3, enrolled, top });
    setLoadingReports(false);
  };

  useEffect(() => { loadCourses(); }, []);

  useEffect(() => {
    if (activeTab === "Users") loadUsers();
    if (activeTab === "Reports") loadReports();
  }, [activeTab]);

  const handleCreateCourse = async (e) => {
    e.preventDefault();
    setCreating(true);
    const r = await createCourse({ ...createForm, lecturerID: parseInt(createForm.lecturerID) });
    if (r.status === 201) {
      setCreateMsg("Course created!");
      setCreateForm({ courseCode:"", courseName:"", department:"", lecturerID:"" });
      loadCourses();
    } else { setCreateMsg(r.error || "Error"); }
    setCreating(false);
    setTimeout(()=>setCreateMsg(null), 4000);
  };

  const handleDeleteCourse = async (courseCode) => {
    const r = await deleteCourse(courseCode);
    if (r.status === 200) {
      setDeleteMsg(`${courseCode} deleted.`);
      if (selectedCourse?.courseCode === courseCode) setSelectedCourse(null);
      loadCourses();
    }
    else setDeleteMsg(r.error || "Delete failed");
    setTimeout(()=>setDeleteMsg(null), 4000);
  };

  const handleSelectCourse = async (course) => {
    setSelectedCourse(course);
    setCourseMembers([]);
    setMembersError(null);
    setLoadingMembers(true);
    try {
      const data = await getCourseMembers(course.courseCode);
      setCourseMembers(Array.isArray(data) ? data : []);
    } catch {
      setMembersError("Could not load course roster.");
    } finally {
      setLoadingMembers(false);
    }
  };

  const handleEnroll = async (e) => {
    e.preventDefault();
    const r = await enrollStudent(enrollForm.courseCode, parseInt(enrollForm.userID));
    setEnrollMsg(r.status === 201 ? "Enrolled!" : r.error || "Error");
    setTimeout(()=>setEnrollMsg(null), 3000);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setRegistering(true);
    setRegResult(null);
    const r = await registerUser(user.email, password, regForm);
    if (r.status === 201) {
      setRegMsg("User created!");
      setRegResult(r);
      setRegForm({ fname:"", lname:"", email:"", accessLvl:"student" });
      loadUsers();
    } else { setRegMsg(r.error || "Error"); }
    setRegistering(false);
    setTimeout(()=>setRegMsg(null), 5000);
  };

  const filteredCourses = courses.filter(c =>
    c.courseCode.toLowerCase().includes(courseSearch.toLowerCase()) ||
    c.courseName.toLowerCase().includes(courseSearch.toLowerCase()) ||
    c.department.toLowerCase().includes(courseSearch.toLowerCase())
  );

  const filteredUsers = users.filter(u =>
    `${u.fname} ${u.lname} ${u.email}`.toLowerCase().includes(userSearch.toLowerCase())
  );

  const students = users.filter(u => u.accessLvl === "student").length;
  const lecturers = users.filter(u => u.accessLvl === "lecturer").length;


  const DEPARTMENTS = [
    "Computer Science","Mathematics","Physics","Chemistry","Biology","Engineering",
    "Economics","Management","Law","Medicine","Psychology","Sociology","History",
    "Literature","Philosophy","Agriculture","Education","Nursing","Architecture","Accounting"
  ];

  const renderContent = () => {
    switch (activeTab) {
      // â”€â”€ DASHBOARD â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
      case "Dashboard":
        return (
          <div className="flex flex-col gap-6">
            <div>
              <h1 className="text-[24px] font-extrabold text-slate-900">Admin Dashboard</h1>
              <p className="text-[13px] text-slate-400 mt-1">System overview and quick stats</p>
            </div>
            <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
              <StatCard icon={BookOpen} label="Total Courses" value={courses.length} color="bg-indigo-100" textColor="text-indigo-600"/>
              <StatCard icon={Users} label="Total Users" value={users.length || "â€”"} color="bg-sky-100" textColor="text-sky-600"/>
              <StatCard icon={GraduationCap} label="Students" value={students||"â€”"} color="bg-emerald-100" textColor="text-emerald-600"/>
              <StatCard icon={BookOpen} label="Lecturers" value={lecturers||"â€”"} color="bg-purple-100" textColor="text-purple-600"/>
            </div>
            <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 flex items-center gap-3">
              <AlertTriangle size={16} className="text-amber-600 shrink-0"/>
              <p className="text-[12px] text-amber-700">
                User counts require visiting the <strong>Users</strong> tab first to load data.
                Navigate there to populate these stats.
              </p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-5">
              <h2 className="text-[15px] font-extrabold text-slate-800 mb-3">Recent Courses</h2>
              {loadingCourses ? <Skeleton className="h-20 w-full rounded-xl"/> :
                <div className="flex flex-col gap-2">
                  {courses.slice(0,5).map(c=>(
                    <div key={c.courseCode} className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2">
                      <div>
                        <span className="text-[12px] font-bold text-slate-700">{c.courseCode}</span>
                        <span className="text-[11px] text-slate-400 ml-2">{c.courseName}</span>
                      </div>
                      <Badge variant="outline" className="text-[10px]">{c.department}</Badge>
                    </div>
                  ))}
                </div>
              }
            </div>
          </div>
        );

      // â”€â”€ COURSES â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
      case "Courses":
        return (
          <div className="flex flex-col gap-6">
            <h1 className="text-[24px] font-extrabold text-slate-900">Course Management</h1>

            {/* Create course */}
            <div className="rounded-xl border border-slate-200 bg-white p-5">
              <h2 className="text-[14px] font-extrabold text-slate-800 mb-4">Create New Course</h2>
              <form onSubmit={handleCreateCourse} className="flex flex-col gap-3">
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label className="text-[12px] font-semibold text-slate-600">Course Code (8 chars)</Label>
                    <Input placeholder="COMP3161" value={createForm.courseCode}
                      onChange={e=>setCreateForm(p=>({...p,courseCode:e.target.value.toUpperCase()}))}
                      maxLength={8} required className="h-9 text-[13px]"/>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-[12px] font-semibold text-slate-600">Course Name</Label>
                    <Input placeholder="Database Management" value={createForm.courseName}
                      onChange={e=>setCreateForm(p=>({...p,courseName:e.target.value}))} required className="h-9 text-[13px]"/>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label className="text-[12px] font-semibold text-slate-600">Department</Label>
                    <Select value={createForm.department} onValueChange={v=>setCreateForm(p=>({...p,department:v}))}>
                      <SelectTrigger className="h-9 text-[13px]"><SelectValue placeholder="Select department"/></SelectTrigger>
                      <SelectContent>{DEPARTMENTS.map(d=><SelectItem key={d} value={d}>{d}</SelectItem>)}</SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-[12px] font-semibold text-slate-600">Lecturer ID</Label>
                    <Input type="number" placeholder="200000000" value={createForm.lecturerID}
                      onChange={e=>setCreateForm(p=>({...p,lecturerID:e.target.value}))} required className="h-9 text-[13px]"/>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Button type="submit" disabled={creating} className="h-9 gap-1 bg-indigo-600 hover:bg-indigo-700">
                    <Plus size={14}/> Create Course
                  </Button>
                  {createMsg && <p className={`text-[12px] font-semibold ${createMsg.includes("!")||createMsg.includes("success")?"text-emerald-600":"text-red-500"}`}>{createMsg}</p>}
                </div>
              </form>
            </div>

            {/* Enroll student */}
            <div className="rounded-xl border border-slate-200 bg-white p-5">
              <h2 className="text-[14px] font-extrabold text-slate-800 mb-4">Enroll Student</h2>
              <form onSubmit={handleEnroll} className="flex gap-3 flex-wrap items-end">
                <div className="space-y-1">
                  <Label className="text-[12px] font-semibold text-slate-600">Course Code</Label>
                  <Input placeholder="COMP3161" value={enrollForm.courseCode}
                    onChange={e=>setEnrollForm(p=>({...p,courseCode:e.target.value.toUpperCase()}))} className="h-9 text-[13px] w-[160px]"/>
                </div>
                <div className="space-y-1">
                  <Label className="text-[12px] font-semibold text-slate-600">Student ID</Label>
                  <Input type="number" placeholder="620000000" value={enrollForm.userID}
                    onChange={e=>setEnrollForm(p=>({...p,userID:e.target.value}))} className="h-9 text-[13px] w-[160px]"/>
                </div>
                <Button type="submit" className="h-9 gap-1 bg-emerald-600 hover:bg-emerald-700">
                  <UserPlus size={14}/> Enroll
                </Button>
                {enrollMsg && <p className={`text-[12px] font-semibold ${enrollMsg==="Enrolled!"?"text-emerald-600":"text-red-500"}`}>{enrollMsg}</p>}
              </form>
            </div>

            {/* Course list */}
            <div className="flex flex-col gap-3">
              {selectedCourse && (
                <CourseRosterPanel
                  course={selectedCourse}
                  members={courseMembers}
                  loading={loadingMembers}
                  error={membersError}
                  onBack={() => setSelectedCourse(null)}
                />
              )}
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 flex-1 max-w-[340px]">
                  <Search size={14} className="text-slate-400 shrink-0"/>
                  <Input placeholder="Search courses..." value={courseSearch} onChange={e=>setCourseSearch(e.target.value)}
                    className="h-auto border-none p-0 text-[13px] shadow-none focus-visible:ring-0"/>
                </div>
                <span className="text-[12px] text-slate-400">{filteredCourses.length} courses</span>
              </div>
              {deleteMsg && <p className={`text-[12px] font-semibold ${deleteMsg.includes("deleted")?"text-emerald-600":"text-red-500"}`}>{deleteMsg}</p>}
              {loadingCourses
                ? <div className="flex flex-col gap-2">{[1,2,3].map(i=><Skeleton key={i} className="h-14 w-full rounded-xl"/>)}</div>
                : <div className="rounded-xl border border-slate-200 overflow-hidden">
                    {filteredCourses.map((c,i)=>(
                      <React.Fragment key={c.courseCode}>
                        {i>0&&<Separator/>}
                        <div
                          className={`flex cursor-pointer items-center justify-between px-4 py-3 transition-colors hover:bg-slate-50 ${selectedCourse?.courseCode === c.courseCode ? "bg-indigo-50" : "bg-white"}`}
                          onClick={() => handleSelectCourse(c)}
                        >
                          <div className="flex min-w-0 items-center gap-3">
                            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-100">
                              <BookOpen size={14} className="text-indigo-600"/>
                            </div>
                            <div className="min-w-0">
                              <p className="text-[13px] font-bold text-slate-800">{c.courseCode}: {c.courseName}</p>
                              <p className="text-[11px] text-slate-400">{c.department}</p>
                            </div>
                          </div>
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button size="sm" variant="ghost" onClick={(e)=>e.stopPropagation()} className="h-8 w-8 text-red-400 hover:text-red-600 hover:bg-red-50 p-0">
                                <Trash2 size={14}/>
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>Delete {c.courseCode}?</AlertDialogTitle>
                                <AlertDialogDescription>
                                  This will permanently delete the course and all its calendar events, sections, content, submissions, forums, and discussion threads. This cannot be undone.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                <AlertDialogAction className="bg-red-600 hover:bg-red-700" onClick={()=>handleDeleteCourse(c.courseCode)}>
                                  Delete
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        </div>
                      </React.Fragment>
                    ))}
                  </div>
              }
            </div>
          </div>
        );

      // â”€â”€ USERS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
      case "Users":
        return (
          <div className="flex flex-col gap-6">
            <h1 className="text-[24px] font-extrabold text-slate-900">User Management</h1>

            {/* Register user */}
            <div className="rounded-xl border border-slate-200 bg-white p-5">
              <h2 className="text-[14px] font-extrabold text-slate-800 mb-4">Register New User</h2>
              <form onSubmit={handleRegister} className="flex flex-col gap-3">
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label className="text-[12px] font-semibold text-slate-600">First Name</Label>
                    <Input placeholder="Jane" value={regForm.fname} onChange={e=>setRegForm(p=>({...p,fname:e.target.value}))} required className="h-9 text-[13px]"/>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-[12px] font-semibold text-slate-600">Last Name</Label>
                    <Input placeholder="Doe" value={regForm.lname} onChange={e=>setRegForm(p=>({...p,lname:e.target.value}))} required className="h-9 text-[13px]"/>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label className="text-[12px] font-semibold text-slate-600">Email</Label>
                    <Input type="email" placeholder="jane@example.com" value={regForm.email} onChange={e=>setRegForm(p=>({...p,email:e.target.value}))} required className="h-9 text-[13px]"/>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-[12px] font-semibold text-slate-600">Role</Label>
                    <Select value={regForm.accessLvl} onValueChange={v=>setRegForm(p=>({...p,accessLvl:v}))}>
                      <SelectTrigger className="h-9 text-[13px]"><SelectValue/></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="student">Student</SelectItem>
                        <SelectItem value="lecturer">Lecturer</SelectItem>
                        <SelectItem value="admin">Admin</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="flex items-center gap-3 flex-wrap">
                  <Button type="submit" disabled={registering} className="h-9 gap-1 bg-indigo-600 hover:bg-indigo-700">
                    <UserPlus size={14}/> Register
                  </Button>
                  {regMsg && <p className={`text-[12px] font-semibold ${regMsg==="User created!"?"text-emerald-600":"text-red-500"}`}>{regMsg}</p>}
                </div>
                {regResult && (
                  <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3">
                    <p className="text-[12px] font-bold text-emerald-700 mb-1">Account created successfully</p>
                    <p className="text-[11px] text-emerald-600">User ID: <strong>{regResult.user?.userID}</strong></p>
                    <p className="text-[11px] text-emerald-600">Generated Password: <strong className="font-mono">{regResult.generatedPassword}</strong></p>
                    <p className="text-[10px] text-emerald-500 mt-1">Share this password with the user. They should change it after first login.</p>
                  </div>
                )}
              </form>
            </div>

            {/* User list */}
            <div className="flex flex-col gap-3">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 flex-1 max-w-[340px]">
                  <Search size={14} className="text-slate-400 shrink-0"/>
                  <Input placeholder="Search users..." value={userSearch} onChange={e=>setUserSearch(e.target.value)}
                    className="h-auto border-none p-0 text-[13px] shadow-none focus-visible:ring-0"/>
                </div>
                <Button size="sm" variant="outline" onClick={loadUsers} className="h-9 gap-1 text-[12px]">
                  <RefreshCw size={13}/> Refresh
                </Button>
                <span className="text-[12px] text-slate-400">{filteredUsers.length} users</span>
              </div>
              {loadingUsers
                ? <Skeleton className="h-32 w-full rounded-xl"/>
                : <div className="rounded-xl border border-slate-200 overflow-hidden">
                    {filteredUsers.slice(0,100).map((u,i)=>{
                      const roleColor = {admin:"bg-red-100 text-red-700",lecturer:"bg-indigo-100 text-indigo-700",student:"bg-emerald-100 text-emerald-700"};
                      return <React.Fragment key={u.userID}>
                        {i>0&&<Separator/>}
                        <div className="flex items-center justify-between px-4 py-2.5 bg-white">
                          <div className="flex items-center gap-3">
                            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-100">
                              <span className="text-[10px] font-bold text-slate-500">{u.fname?.[0]}{u.lname?.[0]}</span>
                            </div>
                            <div>
                              <p className="text-[12px] font-bold text-slate-800">{u.fname} {u.lname}</p>
                              <p className="text-[10px] text-slate-400">{u.email} Â· ID: {u.userID}</p>
                            </div>
                          </div>
                          <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold capitalize ${roleColor[u.accessLvl]||"bg-slate-100 text-slate-600"}`}>{u.accessLvl}</span>
                        </div>
                      </React.Fragment>;
                    })}
                    {filteredUsers.length > 100 && (
                      <div className="px-4 py-2 bg-slate-50 text-[11px] text-slate-400 italic">
                        Showing first 100 of {filteredUsers.length} results. Use search to narrow down.
                      </div>
                    )}
                  </div>
              }
            </div>
          </div>
        );

      // â”€â”€ REPORTS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
      case "Reports":
        return (
          <div className="flex flex-col gap-7">
            <div className="flex items-center justify-between">
              <h1 className="text-[24px] font-extrabold text-slate-900">Reports</h1>
              <Button size="sm" variant="outline" onClick={loadReports} className="gap-1 text-[12px]">
                <RefreshCw size={13}/> Reload
              </Button>
            </div>

            {/* Count cards */}
            <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
              <StatCard icon={BookOpen} label="Courses â‰¥50 students" value={reports.c50.length} color="bg-indigo-100" textColor="text-indigo-600"/>
              <StatCard icon={GraduationCap} label="Students â‰¥5 courses" value={reports.s5plus.length} color="bg-emerald-100" textColor="text-emerald-600"/>
              <StatCard icon={Users} label="Lecturers â‰¥3 courses" value={reports.l3.length} color="bg-purple-100" textColor="text-purple-600"/>
              <StatCard icon={TrendingUp} label="Most enrolled" value={reports.enrolled[0]?.courseName ?? "â€”"} color="bg-amber-100" textColor="text-amber-600"/>
            </div>

            <ReportTable
              title="Courses with 50+ Students"
              columns={[{key:"courseCode",label:"Code"},{key:"student_count",label:"Students"}]}
              rows={reports.c50} loading={loadingReports}
            />
            <ReportTable
              title="Students in 5+ Courses"
              columns={[{key:"userID",label:"User ID"},{key:"fname",label:"First"},{key:"lname",label:"Last"},{key:"course_count",label:"Courses"}]}
              rows={reports.s5plus} loading={loadingReports}
            />
            <ReportTable
              title="Lecturers Teaching 3+ Courses"
              columns={[{key:"fname",label:"First"},{key:"lname",label:"Last"},{key:"num_courses",label:"Courses"}]}
              rows={reports.l3} loading={loadingReports}
            />
            <ReportTable
              title="Top 10 Most Enrolled Courses"
              columns={[{key:"courseCode",label:"Code"},{key:"courseName",label:"Name"},{key:"enrollment_count",label:"Enrolled"}]}
              rows={reports.enrolled} loading={loadingReports}
            />
            <ReportTable
              title="Top 10 Students by Average"
              columns={[{key:"userID",label:"ID"},{key:"fname",label:"First"},{key:"lname",label:"Last"},{key:"overall_average",label:"Average"}]}
              rows={reports.top} loading={loadingReports}
            />
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
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab}/>
      <div className="flex flex-1 flex-col gap-6 overflow-y-auto p-8 box-border">{renderContent()}</div>
    </div>
  );
}




