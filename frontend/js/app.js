const API_BASE = window.location.origin;
document.getElementById("healthBtn").addEventListener("click",async()=>{const o=document.getElementById("output");try{const r=await fetch(`${API_BASE}/api/health`);o.textContent=JSON.stringify(await r.json(),null,2)}catch(e){o.textContent=`Backend connection failed: ${e.message}`}});
