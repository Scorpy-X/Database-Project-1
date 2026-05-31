import React, { useState, useEffect } from "react";
import { MessageSquare, Send, ArrowLeft, MessageCircle, CornerDownRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";

import { Badge } from "@/components/ui/badge";
import { getCourseForums, getForumThreads, getThread, createThread, replyToThread } from "@/api";

export default function ForumSection({ courseCode }) {
  const [forums, setForums] = useState([]);
  const [selectedForum, setSelectedForum] = useState(null);
  const [threads, setThreads] = useState([]);
  const [selectedThread, setSelectedThread] = useState(null);
  const [replies, setReplies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingThreads, setLoadingThreads] = useState(false);
  const [newTopic, setNewTopic] = useState("");
  const [newBody, setNewBody] = useState("");
  const [replyBody, setReplyBody] = useState("");
  const [posting, setPosting] = useState(false);

  useEffect(() => {
    setLoading(true);
    getCourseForums(courseCode).then(d=>{setForums(Array.isArray(d)?d:[]);setLoading(false);}).catch(()=>setLoading(false));
  }, [courseCode]);

  const handleSelectForum = (forum) => {
    setSelectedForum(forum); setSelectedThread(null); setLoadingThreads(true);
    getForumThreads(forum.dfID).then(d=>{setThreads(Array.isArray(d)?d:[]);setLoadingThreads(false);}).catch(()=>setLoadingThreads(false));
  };

  const handleSelectThread = (thread) => {
    setSelectedThread(thread);
    getThread(thread.dtID).then(d=>setReplies(d?.replies||[])).catch(()=>setReplies([]));
  };

  const handleCreateThread = async (e) => {
    e.preventDefault(); if (!newBody.trim()) return;
    setPosting(true);
    try {
      await createThread(selectedForum.dfID, newTopic, newBody);
      setNewTopic(""); setNewBody("");
      const d = await getForumThreads(selectedForum.dfID);
      setThreads(Array.isArray(d)?d:[]);
    } catch { setReplies([]); } finally { setPosting(false); }
  };

  const handleCreateReply = async (e) => {
    e.preventDefault(); if (!replyBody.trim()) return;
    setPosting(true);
    try {
      await replyToThread(selectedThread.dtID, replyBody);
      setReplyBody("");
      const d = await getThread(selectedThread.dtID);
      setReplies(d?.replies||[]);
    } catch { setThreads([]); } finally { setPosting(false); }
  };

  if (loading) return <div className="flex flex-col gap-2"><Skeleton className="h-16 w-full rounded-xl"/><Skeleton className="h-16 w-full rounded-xl"/></div>;

  // View A â€” Forum list
  if (!selectedForum) return (
    <div className="flex flex-col gap-3">
      <h2 className="text-[15px] font-extrabold text-slate-900">Course Boards</h2>
      {forums.length===0 ? <p className="text-sm italic text-slate-400">No forums yet.</p> :
        forums.map(f=>(
          <button key={f.dfID} onClick={()=>handleSelectForum(f)}
            className="flex items-center gap-4 rounded-xl border border-slate-200 bg-white p-4 text-left hover:border-indigo-300 hover:bg-indigo-50 transition-all">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-indigo-100">
              <MessageSquare size={18} className="text-indigo-600"/>
            </div>
            <span className="text-[14px] font-bold text-slate-800">{f.dfname}</span>
          </button>
        ))
      }
    </div>
  );

  // View B â€” Thread list
  if (!selectedThread) return (
    <div className="flex flex-col gap-4">
      <Button variant="ghost" size="sm" onClick={()=>setSelectedForum(null)} className="w-fit gap-1 text-indigo-600">
        <ArrowLeft size={14}/> Back to Boards
      </Button>
      <h2 className="text-[18px] font-extrabold text-slate-900">{selectedForum.dfname}</h2>
      <form onSubmit={handleCreateThread} className="flex flex-col gap-2 rounded-xl border border-slate-200 bg-white p-4">
        <Input placeholder="Topic (optional)" value={newTopic} onChange={e=>setNewTopic(e.target.value)} maxLength={20} className="h-9 text-[13px]"/>
        <div className="flex gap-2">
          <Input placeholder="Write a post..." value={newBody} onChange={e=>setNewBody(e.target.value)} maxLength={500} required className="h-9 flex-1 text-[13px]"/>
          <Button type="submit" size="icon" disabled={posting} className="h-9 w-9 shrink-0 bg-indigo-600 hover:bg-indigo-700"><Send size={14}/></Button>
        </div>
      </form>
      {loadingThreads ? <Skeleton className="h-20 w-full rounded-xl"/> :
        threads.length===0 ? <p className="text-sm italic text-slate-400">No threads yet.</p> :
        <div className="flex flex-col gap-2">
          {threads.map(t=>(
            <button key={t.dtID} onClick={()=>handleSelectThread(t)}
              className="flex flex-col gap-2 rounded-xl border border-slate-200 bg-white p-4 text-left hover:border-indigo-300 hover:bg-slate-50 transition-all">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="flex h-7 w-7 items-center justify-center rounded-full bg-indigo-600 text-[10px] font-bold text-white">
                    {t.fname?.[0]}{t.lname?.[0]}
                  </div>
                  <div>
                    <p className="text-[12px] font-bold text-slate-800">{t.fname} {t.lname}</p>
                    <p className="text-[10px] text-slate-400">{t.date_created}</p>
                  </div>
                </div>
                <Badge variant="outline" className="flex items-center gap-1 text-[10px] text-slate-500">
                  <MessageCircle size={10}/> {t.replyCount||0}
                </Badge>
              </div>
              {t.topic && <p className="text-[13px] font-extrabold text-slate-800">{t.topic}</p>}
              <p className="text-[12px] text-slate-600 line-clamp-2">{t.threadbody}</p>
            </button>
          ))}
        </div>
      }
    </div>
  );

  // View C â€” Thread detail + replies
  return (
    <div className="flex flex-col gap-4">
      <Button variant="ghost" size="sm" onClick={()=>setSelectedThread(null)} className="w-fit gap-1 text-indigo-600">
        <ArrowLeft size={14}/> Back to Threads
      </Button>
      <div className="rounded-xl border border-slate-300 bg-slate-50 p-4">
        <div className="mb-3 flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-800 text-[10px] font-bold text-white">
            {selectedThread.fname?.[0]}{selectedThread.lname?.[0]}
          </div>
          <div>
            <p className="text-[12px] font-bold text-slate-800">{selectedThread.fname} {selectedThread.lname}</p>
            <p className="text-[10px] text-slate-400">{selectedThread.date_created}</p>
          </div>
        </div>
        {selectedThread.topic && <h3 className="mb-1 text-[15px] font-extrabold text-slate-900">{selectedThread.topic}</h3>}
        <p className="text-[13px] leading-relaxed text-slate-700">{selectedThread.threadbody}</p>
      </div>
      <div className="flex flex-col gap-2 border-l-2 border-slate-200 pl-4">
        {replies.length===0
          ? <p className="text-[12px] italic text-slate-400">No replies yet.</p>
          : replies.map(r=>(
            <div key={r.dtID} className="flex gap-2 rounded-xl border border-slate-200 bg-white p-3">
              <CornerDownRight size={13} className="mt-1 shrink-0 text-slate-400"/>
              <div className="flex flex-col gap-1">
                <div className="flex items-center gap-2">
                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-slate-400 text-[9px] font-bold text-white">{r.fname?.[0]}{r.lname?.[0]}</div>
                  <span className="text-[12px] font-bold text-slate-700">{r.fname} {r.lname}</span>
                  <span className="text-[10px] text-slate-400">{r.date_created}</span>
                </div>
                <p className="text-[12px] leading-relaxed text-slate-600">{r.threadbody}</p>
              </div>
            </div>
          ))
        }
      </div>
      <form onSubmit={handleCreateReply} className="flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-3 py-2">
        <Input placeholder={`Reply to ${selectedThread.fname}...`} value={replyBody} onChange={e=>setReplyBody(e.target.value)}
          maxLength={500} required className="h-8 flex-1 border-none text-[13px] shadow-none focus-visible:ring-0"/>
        <Button type="submit" size="icon" disabled={posting} className="h-8 w-8 shrink-0 bg-indigo-600 hover:bg-indigo-700">
          <Send size={13}/>
        </Button>
      </form>
    </div>
  );
}



