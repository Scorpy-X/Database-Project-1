import { useState } from "react";
import { Eye, EyeOff, GraduationCap } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { loginUser } from "@/api";

export default function Login() {
  const navigate = useNavigate();
  const [showPw, setShowPw] = useState(false);
  const [remember, setRemember] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    let result;
    try {
      result = await loginUser(email, password);
    } catch {
      result = { status: 0, error: "Unable to contact the backend. Check that Flask is running." };
    } finally {
      setLoading(false);
    }

    if (result.status === 200) {
      const store = remember ? localStorage : sessionStorage;
      store.setItem("user", JSON.stringify({ ...result.user, email }));
      store.setItem("password", password);

      const role = result.user.accessLvl;
      if (role === "admin") navigate("/dashboard/admin");
      else if (role === "lecturer") navigate("/dashboard/lecturer");
      else navigate("/dashboard/student");
    } else {
      setError(result.error || "Invalid credentials.");
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-white">
      {/* Left panel */}
      <div className="relative hidden w-1/2 lg:block">
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-700 to-sky-500" />
        <div className="absolute left-8 top-8 z-10 flex items-center gap-3">
          <GraduationCap className="h-9 w-9 text-white drop-shadow" />
          <span className="font-['Playfair_Display'] text-[22px] font-bold text-white">StudEx</span>
        </div>
        <div className="absolute bottom-14 left-8 right-8 z-10">
          <h2 className="font-['Playfair_Display'] mb-3 text-[30px] font-black uppercase tracking-[4px] text-white">
            Welcome Back
          </h2>
          <p className="text-[14px] leading-relaxed text-white/80">
            Your virtual learning environment. Access courses, assignments, forums, and more.
          </p>
        </div>
      </div>

      {/* Right form */}
      <div className="flex w-full flex-col items-center justify-center overflow-y-auto bg-white px-8 py-12 lg:w-1/2">
        <div className="w-full max-w-[400px]">
          <h1 className="font-['Playfair_Display'] mb-1.5 text-[34px] font-extrabold text-slate-900">Login</h1>
          <p className="font-['DM_Sans'] mb-8 text-[13.5px] text-slate-500">
            Sign in to your account to continue.
          </p>

          {error && (
            <div className="mb-5 rounded-lg border border-red-100 bg-red-50 px-4 py-3 text-[13.5px] text-red-600">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex flex-col gap-5">
            <div className="space-y-1.5">
              <Label htmlFor="email" className="text-[13.5px] font-semibold text-slate-700">Email</Label>
              <Input id="email" type="email" placeholder="you@example.com" value={email}
                onChange={(e) => setEmail(e.target.value)} required
                className="h-11 rounded-lg border-slate-200 bg-slate-50 text-sm focus-visible:ring-indigo-400" />
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="password" className="text-[13.5px] font-semibold text-slate-700">Password</Label>
              <div className="relative">
                <Input id="password" type={showPw ? "text" : "password"} placeholder="Your password"
                  value={password} onChange={(e) => setPassword(e.target.value)} required
                  className="h-11 rounded-lg border-slate-200 bg-slate-50 pr-11 text-sm focus-visible:ring-indigo-400" />
                <Button type="button" variant="ghost" size="icon" onClick={() => setShowPw(v => !v)}
                  className="absolute right-1 top-1/2 h-8 w-8 -translate-y-1/2 text-slate-400">
                  {showPw ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Checkbox id="remember" checked={remember} onCheckedChange={v => setRemember(Boolean(v))}
                  className="border-slate-300 data-[state=checked]:border-indigo-500 data-[state=checked]:bg-indigo-500" />
                <Label htmlFor="remember" className="cursor-pointer text-[13.5px] text-slate-600">Remember me</Label>
              </div>
            </div>

            <Button type="submit" disabled={loading}
              className="h-11 w-full rounded-xl bg-gradient-to-r from-indigo-500 to-sky-500 text-[15px] font-bold text-white disabled:opacity-60">
              {loading ? "Signing in..." : "Sign In"}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
