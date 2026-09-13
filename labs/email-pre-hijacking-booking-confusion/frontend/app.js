const $=id=>document.getElementById(id);let user=null;let patched=false;
async function api(path,options={}){const r=await fetch(path,{credentials:"include",headers:{"Content-Type":"application/json"},...options});const d=await r.json().catch(()=>({}));if(!r.ok)throw Error(d.error||`HTTP ${r.status}`);return d}
function render(){ $("auth").hidden=!!user;$("app").hidden=!user;if(user){$("email").textContent=user.email;$("status").textContent=user.email_verified?"Email verified":"Email unverified";$("bookingEmail").value=user.email}}
function renderMode(){$("mode").textContent=patched?"Patched mode":"Vulnerable mode";$("mode").style.background=patched?"#173d31":"#4b2b20"}
async function refresh(){try{const d=await api("/api/me");user=d.user;patched=d.patched_mode;renderMode();render();await load()}catch{user=null;render()}}
async function load(){const d=await api("/api/bookings");$("list").innerHTML=d.bookings.length?d.bookings.map(b=>`<div class="booking-card"><b>${b.hotel} — ${b.room}</b><div>${b.guest_name}</div><div>${b.check_in} → ${b.check_out}</div><small>Reference: ${b.reference}<br>Booking email: ${b.email}</small></div>`).join(""):"<p>No bookings.</p>"}
function msg(t){$("message").textContent=t}
$("register").onsubmit=async e=>{e.preventDefault();try{await api("/api/register",{method:"POST",body:JSON.stringify({email:$("regEmail").value,password:$("regPassword").value})});msg("Account created; email is unverified.");await refresh()}catch(x){msg(x.message)}}
$("login").onsubmit=async e=>{e.preventDefault();try{await api("/api/login",{method:"POST",body:JSON.stringify({email:$("loginEmail").value,password:$("loginPassword").value})});msg("Logged in.");await refresh()}catch(x){msg(x.message)}}
$("logout").onclick=async()=>{await api("/api/logout",{method:"POST"});user=null;render();msg("Logged out.")}
$("verify").onclick=async()=>{try{await api("/api/verify-email",{method:"POST"});await refresh();msg("Synthetic email verified.")}catch(x){msg(x.message)}}
$("booking").onsubmit=async e=>{e.preventDefault();try{const d=await api("/api/bookings",{method:"POST",body:JSON.stringify({guest_name:$("guest").value,email:$("bookingEmail").value,hotel:$("hotel").value,room:$("room").value,check_in:$("checkin").value,check_out:$("checkout").value})});msg("Booking created: "+d.reference);await load()}catch(x){msg(x.message)}}
async function setMode(value){try{const d=await api("/api/lab/mode",{method:"POST",body:JSON.stringify({patched_mode:value})});patched=d.patched_mode;renderMode();msg(patched?"Patched mode enabled.":"Vulnerable mode enabled.")}catch(x){msg(x.message)}}
$("vulnerable").onclick=()=>setMode(false);$("patched").onclick=()=>setMode(true);
$("reset").onclick=async()=>{if(confirm("Reset all users and bookings?")){await api("/api/lab/reset",{method:"POST"});user=null;patched=false;renderMode();render();msg("Lab reset.")}}
refresh();
