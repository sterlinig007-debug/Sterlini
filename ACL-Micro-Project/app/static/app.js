const modal=document.getElementById("modal");
const form=document.getElementById("record-form");
function openCreate(){
  document.getElementById("modal-title").textContent="New Record";
  document.getElementById("record-id").value="";
  form.reset(); modal.classList.remove("hidden");
}
function openEdit(r){
  document.getElementById("modal-title").textContent="Edit Record";
  document.getElementById("record-id").value=r.id;
  for(const k of ["student_name","faculty_name","email","phone_number","description"])
    document.getElementById(k).value=r[k];
  document.getElementById("branch_form").value=r.branch;
  modal.classList.remove("hidden");
}
function closeModal(){modal.classList.add("hidden")}
form.addEventListener("submit",async e=>{
  e.preventDefault();
  const id=document.getElementById("record-id").value;
  const payload={
    student_name:document.getElementById("student_name").value,
    faculty_name:document.getElementById("faculty_name").value,
    branch:document.getElementById("branch_form").value,
    email:document.getElementById("email").value,
    phone_number:document.getElementById("phone_number").value,
    description:document.getElementById("description").value
  };
  const res=await fetch(id?`/api/records/${id}`:"/api/records",{
    method:id?"PUT":"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)
  });
  if(!res.ok){alert((await res.json()).detail||"Operation failed");return}
  location.reload();
});
async function deleteRecord(id){
  if(!confirm("Delete this record?")) return;
  const res=await fetch(`/api/records/${id}`,{method:"DELETE"});
  if(!res.ok){alert((await res.json()).detail||"Delete failed");return}
  location.reload();
}
async function explainAccess(){
  const operation=document.getElementById("operation").value;
  const branch=document.getElementById("branch").value||null;
  const out=document.getElementById("explanation");
  out.textContent="Checking ACL...";
  const res=await fetch("/api/access/explain",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({operation,branch})});
  const data=await res.json();
  if(!res.ok){out.textContent=data.detail||"Error";return}
  out.textContent=`Decision: ${data.decision?"GRANTED":"DENIED"}\n\nRule: ${data.deterministic_reason}\n\nAI/LLM explanation:\n${data.ai_explanation}`;
}
