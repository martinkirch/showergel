import{_ as v,h as u,d as h,o as i,c as d,b as e,w as m,f as b,F as S,r as g,t as p,v as f,e as _,n as y,j as $,i as k}from"./index.49246efe.js";import{n as w}from"./notifications.b7f906af.js";import{s as E,f as x}from"./vue3-datepicker.esm.82138076.js";const D={props:["parameters"],components:{Datepicker:E},data(){return{template:"",day:new Date,time:x(new Date,"HH:mm:ss"),command:""}},watch:{template(s){this.command=s}},methods:{addEvent(){let s=new Date(this.day),t=this.time.split(":"),l=parseInt(t[0]);(l||l===0)&&s.setHours(l);let r=parseInt(t[1]);(r||r===0)&&s.setMinutes(r);let n=parseInt(t[2]);(n||n===0)&&s.setSeconds(n),u.put("/schedule",{command:this.command,when:s.toISOString()}).then(this.getSchedule).catch(w.error_handler(error))}}},C={class:"field"},V=e("label",{class:"label",for:"template"},"Command template",-1),L={class:"select"},U=e("option",{selected:"",disabled:"",value:""},"Pick a command... ",-1),I=["value"],M={class:"field"},R=e("label",{class:"label",for:"command"},"Command",-1),B={class:"control"},H=e("label",{class:"label",for:"day"},"When",-1),N={class:"field has-addons"},z={class:"control"},A={class:"control"},F={class:"field"};function T(s,t,l,r,n,c){const a=h("Datepicker");return i(),d("form",{onSubmit:t[4]||(t[4]=$(o=>c.addEvent(),["prevent"])),class:"box"},[e("div",C,[V,e("div",L,[m(e("select",{"onUpdate:modelValue":t[0]||(t[0]=o=>n.template=o),id:"template"},[U,(i(!0),d(S,null,g(l.parameters.commands,o=>(i(),d("option",{key:o,value:o},p(o),9,I))),128))],512),[[b,n.template]])])]),e("div",M,[R,e("div",B,[m(e("input",{type:"text",class:"input","onUpdate:modelValue":t[1]||(t[1]=o=>n.command=o)},null,512),[[f,n.command]])])]),H,e("div",N,[e("div",z,[_(a,{class:"input",placeholder:"2021-01-01",modelValue:n.day,"onUpdate:modelValue":t[2]||(t[2]=o=>n.day=o)},null,8,["modelValue"])]),e("div",A,[m(e("input",{type:"text",class:"input",size:"8","onUpdate:modelValue":t[3]||(t[3]=o=>n.time=o)},null,512),[[f,n.time]])])]),e("div",F,[e("button",{class:y(`button is-link ${s.isLoading?"is-loading":""}`),type:"submit"}," Add event ",2)])],32)}var j=v(D,[["render",T]]);const O={data(){return{events:null,isLoading:!0,isError:!1}},methods:{onError(s){this.isError=!0,w.error_handler(s)},getSchedule(){this.isLoading=!0,this.isError=!1,u.get("/schedule").then(this.onResults).catch(this.onError)},onResults(s){this.events=s.data.schedule,this.isLoading=!1},deleteEvent(s,t){const l=new Date(t).toLocaleString();confirm(`Really remove event of ${l}?`)&&u.delete("/schedule/"+s).then(this.getSchedule).catch(this.onError)}},mounted(){this.getSchedule()}},P={class:"when"},W=["onClick"],q=e("i",{class:"mdi mdi-calendar-remove"},null,-1),G=[q];function J(s,t,l,r,n,c){return i(),d("div",null,[(i(!0),d(S,null,g(n.events,a=>(i(),d("div",{key:a.id},[e("p",null,[e("span",P,p(new Date(a.when).toLocaleString()),1),k(" "+p(a.what)+" ",1),e("button",{class:"button is-danger icon",onClick:o=>c.deleteEvent(a.event_id,a.when),title:"Remove event"},G,8,W)])]))),128))])}var K=v(O,[["render",J]]);const Q={props:["parameters"],components:{ScheduleCommand:j,Schedule:K}},X={id:"schedule",class:"content my-4"},Y=e("h2",null,"Add an event",-1),Z=e("h2",null,"Upcoming events",-1);function ee(s,t,l,r,n,c){const a=h("ScheduleCommand"),o=h("Schedule",!0);return i(),d("div",X,[Y,_(a,{parameters:l.parameters},null,8,["parameters"]),Z,_(o)])}var oe=v(Q,[["render",ee]]);export{oe as default};