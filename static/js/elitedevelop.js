(() => {
"use strict";


const C = window.ED_CONFIG || {};

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];


/* =========================================================
   TOASTS
   ========================================================= */

const toast = (message, type = "info") => {

    const box = $("#ed-toast-container");

    if (!box) return;

    const el = document.createElement("div");

    el.className = `ed-toast ${type}`;

    const icon =
        type === "success"
            ? "fa-circle-check"
            : type === "error"
                ? "fa-circle-exclamation"
                : "fa-circle-info";

    el.innerHTML = `
        <i class="fa-solid ${icon}"></i>
        <span></span>
    `;

    $("span", el).textContent = message;

    box.appendChild(el);

    setTimeout(() => {

        el.style.opacity = "0";
        el.style.transform = "translateY(8px)";

        setTimeout(() => el.remove(), 180);

    }, 3000);
};

window.edToast = toast;


/* =========================================================
   THEME
   ========================================================= */

function setTheme(theme) {

    document.documentElement.dataset.theme = theme;

    document.documentElement.classList.toggle(
        "dark-theme",
        theme === "dark"
    );

    document.documentElement.style.colorScheme = theme;

    localStorage.setItem("theme", theme);

    const icon = $("#ed-theme-toggle i");

    if (icon) {
        icon.className =
            `fa-solid ${theme === "dark" ? "fa-sun" : "fa-moon"}`;
    }

    const meta = $("#ed-theme-color");

    if (meta) {
        meta.content =
            theme === "dark"
                ? "#0b1220"
                : "#f6f8fc";
    }
}


setTheme(
    localStorage.getItem("theme") ||
    (
        matchMedia("(prefers-color-scheme: dark)").matches
            ? "dark"
            : "light"
    )
);


$("#ed-theme-toggle")?.addEventListener("click", () => {

    const next =
        document.documentElement.classList.contains("dark-theme")
            ? "light"
            : "dark";

    setTheme(next);

    toast(
        `${next === "dark" ? "Dark" : "Light"} mode enabled.`,
        "success"
    );
});


/* =========================================================
   DESKTOP DROPDOWNS
   ========================================================= */

$$(".ed-dropdown").forEach(d => {

    const trigger = $(".ed-dropdown-trigger", d);
    const menu = $(".ed-dropdown-menu", d);

    trigger?.addEventListener("click", e => {

        e.stopPropagation();

        $$(".ed-dropdown-menu.show").forEach(x => {

            if (x !== menu) {
                x.classList.remove("show");
            }

        });

        $$(".ed-dropdown-trigger.open").forEach(x => {

            if (x !== trigger) {
                x.classList.remove("open");
            }

        });

        menu?.classList.toggle("show");
        trigger?.classList.toggle("open");

    });

});


document.addEventListener("click", e => {

    if (!e.target.closest(".ed-dropdown")) {

        $$(".ed-dropdown-menu.show").forEach(x =>
            x.classList.remove("show")
        );

        $$(".ed-dropdown-trigger.open").forEach(x =>
            x.classList.remove("open")
        );

    }

});


/* =========================================================
   MOBILE NAVIGATION
   ========================================================= */

const mobileToggle = $("#ed-mobile-toggle");
const mobilePanel = $("#ed-mobile-panel");


mobileToggle?.addEventListener("click", e => {

    e.stopPropagation();

    const open = mobilePanel?.classList.toggle("open");

    mobileToggle.setAttribute(
        "aria-expanded",
        open ? "true" : "false"
    );

    mobileToggle.innerHTML = `
        <i class="fa-solid ${open ? "fa-xmark" : "fa-bars"}"></i>
    `;

});


$$(".ed-mobile-link").forEach(link => {

    link.addEventListener("click", () => {

        mobilePanel?.classList.remove("open");

        mobileToggle?.setAttribute(
            "aria-expanded",
            "false"
        );

        if (mobileToggle) {
            mobileToggle.innerHTML =
                '<i class="fa-solid fa-bars"></i>';
        }

    });

});


/* =========================================================
   COMMAND PALETTE
   ========================================================= */

const overlay = $("#ed-command-overlay");
const input = $("#ed-command-input");
const items = $$(".ed-command-item");


function openPalette() {

    if (!overlay) return;

    overlay.classList.add("open");

    overlay.setAttribute(
        "aria-hidden",
        "false"
    );

    if (input) {

        input.value = "";

        items.forEach(item => {
            item.style.display = "";
        });

        setTimeout(() => input.focus(), 20);

    }

}


function closePalette() {

    overlay?.classList.remove("open");

    overlay?.setAttribute(
        "aria-hidden",
        "true"
    );

}


$("#ed-command-button")?.addEventListener(
    "click",
    openPalette
);


overlay?.addEventListener("click", e => {

    if (e.target === overlay) {
        closePalette();
    }

});


input?.addEventListener("input", () => {

    const q = input.value.trim().toLowerCase();

    items.forEach(item => {

        item.style.display =
            !q ||
            item.textContent.toLowerCase().includes(q)
                ? ""
                : "none";

    });

});


/* =========================================================
   KEYBOARD SHORTCUTS
   ========================================================= */

document.addEventListener("keydown", e => {

    if (
        (e.ctrlKey || e.metaKey) &&
        e.key.toLowerCase() === "k"
    ) {

        e.preventDefault();
        openPalette();

    }


    if (
        (e.ctrlKey || e.metaKey) &&
        e.shiftKey &&
        e.key.toLowerCase() === "e"
    ) {

        e.preventDefault();

        showSecret("keyboard");

    }


    if (e.key === "Escape") {

        closePalette();

        $$(".ed-dropdown-menu.show").forEach(x =>
            x.classList.remove("show")
        );

        $$(".ed-dropdown-trigger.open").forEach(x =>
            x.classList.remove("open")
        );

    }

});


/* =========================================================
   EXTERNAL LINKS
   ========================================================= */

$$('a[target="_blank"]').forEach(a => {

    a.rel = "noopener noreferrer";

});


/* =========================================================
   EASTER EGGS
   ========================================================= */


/* 7-click logo */

let logoClicks = 0;
let logoTimer;


$("#ed-logo")?.addEventListener("click", e => {

    logoClicks++;

    clearTimeout(logoTimer);

    logoTimer = setTimeout(() => {

        logoClicks = 0;

    }, 1800);


    if (logoClicks === 7) {

        e.preventDefault();

        logoClicks = 0;

        clearTimeout(logoTimer);

        showSecret("logo");

    }

});


/* Secret panel */

function showSecret(reason) {

    $("#ed-secret-panel")?.remove();

    const el = document.createElement("div");

    el.id = "ed-secret-panel";
    el.className = "ed-secret-panel";


    const reasonText =
        reason === "logo"
            ? "7-click logo"
            : reason === "keyboard"
                ? "keyboard"
                : "Konami";


    el.innerHTML = `
        <div>
            <strong>Elite Mode unlocked.</strong>

            <button
                type="button"
                class="btn-close btn-close-white float-end"
                aria-label="Close"
            ></button>
        </div>

        <div
            class="small mt-1"
            style="color:#94a3b8"
        >
            You found the ${reasonText} Easter egg.
        </div>

        <div class="ed-secret-grid">

            <div class="ed-secret-stat">
                <small>Theme</small>
                <b>
                    ${
                        document.documentElement.classList.contains(
                            "dark-theme"
                        )
                            ? "Dark"
                            : "Light"
                    }
                </b>
            </div>

            <div class="ed-secret-stat">
                <small>Viewport</small>
                <b>${innerWidth}×${innerHeight}</b>
            </div>

            <div class="ed-secret-stat">
                <small>Online</small>
                <b>${navigator.onLine ? "Yes" : "No"}</b>
            </div>

            <div class="ed-secret-stat">
                <small>Engine</small>
                <b>
                    ${
                        navigator.userAgent.includes("AppleWebKit")
                            ? "WebKit"
                            : "Browser"
                    }
                </b>
            </div>

        </div>
    `;


    document.body.appendChild(el);


    $(".btn-close", el)?.addEventListener(
        "click",
        () => el.remove()
    );


    setTimeout(() => {

        el.remove();

    }, 10000);

}


/* Konami code */

const konami = [
    "ArrowUp",
    "ArrowUp",
    "ArrowDown",
    "ArrowDown",
    "ArrowLeft",
    "ArrowRight",
    "ArrowLeft",
    "ArrowRight",
    "b",
    "a"
];


let kp = 0;


document.addEventListener("keydown", e => {

    const key =
        e.key.length === 1
            ? e.key.toLowerCase()
            : e.key;


    if (key === konami[kp]) {

        kp++;

        if (kp === konami.length) {

            kp = 0;

            showSecret("Konami");

        }

    } else {

        kp = 0;

    }

});


/* =========================================================
   ACTIVE NAVIGATION
   ========================================================= */

const path =
    location.pathname.replace(/\/+$/, "") || "/";


$$(".ed-nav-link").forEach(a => {

    try {

        const p =
            new URL(
                a.href,
                location.origin
            ).pathname.replace(/\/+$/, "") || "/";

        if (p === path) {
            a.classList.add("active");
        }

    } catch {}

});


/* =========================================================
   DAILY STREAK
   ========================================================= */

if (C.csrfToken) {

    let seconds = Number(C.secondsToday) || 0;

    let earned =
        C.streakEarnedToday === true;


    const timer = $("#nav-streak-timer");
    const count = $("#nav-streak-count");
    const status = $("#nav-streak-status");


    const fmt = s =>
        `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(
            s % 60
        ).padStart(2, "0")}`;


    const update = () => {

        if (timer && !earned) {
            timer.textContent = fmt(seconds);
        }

    };


    update();


    setInterval(() => {

        if (!document.hidden && !earned) {

            seconds++;

            update();

        }

    }, 1000);


    async function sync() {

        if (earned) return;

        try {

            const fd = new FormData();

            fd.append(
                "seconds",
                seconds
            );


            const r = await fetch(
                C.trackTimeURL,
                {
                    method: "POST",

                    headers: {
                        "X-CSRFToken": C.csrfToken,
                        "X-Requested-With": "XMLHttpRequest"
                    },

                    body: fd,

                    credentials: "same-origin"
                }
            );


            if (!r.ok) return;


            const d = await r.json();


            if (d.seconds_today !== undefined) {

                seconds =
                    Number(d.seconds_today);

                update();

            }


            if (
                d.current_streak !== undefined &&
                count
            ) {

                count.textContent =
                    `${d.current_streak}d`;

            }


            if (d.streak_earned_today) {

                earned = true;

                if (status) {

                    status.innerHTML = `
                        <span class="ed-streak-earned">
                            <i class="fa-solid fa-circle-check"></i>
                            Earned
                        </span>
                    `;

                }

                toast(
                    "Daily streak earned!",
                    "success"
                );

            }

        } catch (e) {

            console.warn(
                "EliteDevelop streak:",
                e
            );

        }

    }


    setInterval(sync, 5000);

    sync();


    document.addEventListener(
        "visibilitychange",
        () => {

            if (
                document.hidden &&
                !earned
            ) {

                const fd = new FormData();

                fd.append(
                    "seconds",
                    seconds
                );

                fd.append(
                    "csrfmiddlewaretoken",
                    C.csrfToken
                );


                try {

                    navigator.sendBeacon(
                        C.trackTimeURL,
                        fd
                    );

                } catch {}

            }

        }
    );


    /* =====================================================
       CODE VAULT
       ===================================================== */

    const container =
        $("#vault-list-container");

    const save =
        $("#btn-save-snippet");

    const title =
        $("#snippet-title");

    const lang =
        $("#snippet-lang");

    const code =
        $("#snippet-code");


    const esc = value => {

        const d =
            document.createElement("div");

        d.textContent =
            String(value ?? "");

        return d.innerHTML;

    };


    async function loadVault() {

        if (!container) return;


        container.innerHTML = `
            <div class="vault-empty">
                <i class="fa-solid fa-spinner fa-spin"></i>
                Loading vault...
            </div>
        `;


        try {

            const r = await fetch(
                C.vaultListURL,
                {
                    credentials: "same-origin"
                }
            );


            if (!r.ok) throw 0;


            const d = await r.json();


            container.innerHTML = "";


            if (!d.snippets?.length) {

                container.innerHTML = `
                    <div class="vault-empty">
                        <i class="fa-solid fa-box-open"></i>

                        <div>
                            No snippets yet.
                        </div>

                        <small>
                            Save your first piece of code above.
                        </small>
                    </div>
                `;

                return;

            }


            d.snippets.forEach(s => {

                const card =
                    document.createElement("div");

                card.className =
                    "vault-card";


                const url =
                    new URL(
                        s.share_url,
                        location.origin
                    ).href;


                card.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center gap-2">

                        <div class="min-w-0">

                            <div class="vault-snippet-title">
                                ${esc(s.title || "Untitled")}
                            </div>

                            <div class="vault-meta">
                                ${esc(
                                    (s.language || "text").toUpperCase()
                                )}
                                ${s.date ? " • " + esc(s.date) : ""}
                            </div>

                        </div>

                        <button
                            class="vault-copy"
                            type="button"
                        >
                            <i class="fa-solid fa-link"></i>
                        </button>

                    </div>
                `;


                $(".vault-copy", card)
                    .addEventListener(
                        "click",
                        async () => {

                            try {

                                await navigator.clipboard.writeText(
                                    url
                                );

                                toast(
                                    "Share link copied.",
                                    "success"
                                );

                            } catch {

                                toast(
                                    "Could not copy the link.",
                                    "error"
                                );

                            }

                        }
                    );


                container.appendChild(card);

            });


        } catch {

            container.innerHTML = `
                <div class="vault-empty">
                    <i class="fa-solid fa-triangle-exclamation"></i>

                    <div>
                        Vault unavailable.
                    </div>

                    <small>
                        Try refreshing the panel.
                    </small>
                </div>
            `;

        }

    }


    save?.addEventListener(
        "click",
        async () => {

            if (!code.value.trim()) {

                toast(
                    "Code cannot be empty.",
                    "error"
                );

                code.focus();

                return;

            }


            const old =
                save.innerHTML;


            save.disabled = true;

            save.innerHTML = `
                <i class="fa-solid fa-spinner fa-spin me-1"></i>
                Encrypting...
            `;


            try {

                const r = await fetch(
                    C.vaultSaveURL,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json",

                            "X-CSRFToken":
                                C.csrfToken
                        },

                        credentials:
                            "same-origin",

                        body: JSON.stringify({
                            title:
                                title.value.trim(),

                            language:
                                lang.value,

                            code:
                                code.value
                        })
                    }
                );


                const d =
                    await r.json();


                if (
                    !r.ok ||
                    d.status !== "success"
                ) {
                    throw 0;
                }


                title.value = "";
                code.value = "";


                save.innerHTML = `
                    <i class="fa-solid fa-circle-check me-1"></i>
                    Saved
                `;


                toast(
                    "Snippet encrypted and saved.",
                    "success"
                );


                await loadVault();


                setTimeout(() => {

                    save.innerHTML = old;
                    save.disabled = false;

                }, 1200);


            } catch {

                save.innerHTML = old;
                save.disabled = false;

                toast(
                    "Could not save the snippet.",
                    "error"
                );

            }

        }
    );


    $("#codeVault")
        ?.addEventListener(
            "show.bs.offcanvas",
            loadVault
        );


    $("#vault-refresh")
        ?.addEventListener(
            "click",
            loadVault
        );


    /* =====================================================
       PWA
       ===================================================== */

    const key =
        new Uint8Array(
            C.publicVapidKey || []
        );


    const isStandalone =
        matchMedia(
            "(display-mode: standalone)"
        ).matches ||
        navigator.standalone === true;


    const isIOS =
        /iPad|iPhone|iPod/.test(
            navigator.userAgent
        ) ||
        (
            navigator.platform === "MacIntel" &&
            navigator.maxTouchPoints > 1
        );


    let deferred = null;


    if (!isStandalone && !isIOS) {

        window.addEventListener(
            "beforeinstallprompt",
            e => {

                e.preventDefault();

                deferred = e;

                $("#pwa-install-banner")
                    ?.classList.remove("d-none");

                $("#btn-pwa-install")
                    ?.classList.remove("d-none");

            }
        );

    }


    if (!isStandalone && isIOS) {

        $("#pwa-install-banner")
            ?.classList.remove("d-none");

        $("#ios-install-instructions")
            ?.classList.remove("d-none");

    }


    $("#btn-pwa-install")
        ?.addEventListener(
            "click",
            async () => {

                if (!deferred) return;

                deferred.prompt();

                await deferred.userChoice;

                deferred = null;

                $("#pwa-install-banner")
                    ?.classList.add("d-none");

            }
        );


    /* =====================================================
       PUSH NOTIFICATIONS
       ===================================================== */

    async function saveSub(sub) {

        const r = await fetch(
            C.saveSubscriptionURL,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json",

                    "X-CSRFToken":
                        C.csrfToken
                },

                credentials:
                    "same-origin",

                body:
                    JSON.stringify(sub)
            }
        );


        if (!r.ok) {
            throw Error(
                `Subscription HTTP ${r.status}`
            );
        }

    }


    if ("serviceWorker" in navigator) {

        navigator.serviceWorker
            .register("/sw.js")
            .then(async reg => {

                if (!("PushManager" in window)) {
                    return;
                }


                if (
                    Notification.permission === "default" &&
                    (!isIOS || isStandalone)
                ) {

                    $("#notification-permission-banner")
                        ?.classList.remove("d-none");

                }


                if (
                    Notification.permission === "granted"
                ) {

                    const sub =
                        await reg.pushManager
                            .getSubscription();


                    if (sub) {
                        await saveSub(sub);
                    }

                }


                $("#btn-grant-notifications")
                    ?.addEventListener(
                        "click",
                        async e => {

                            e.currentTarget.disabled =
                                true;


                            try {

                                const sub =
                                    await reg.pushManager
                                        .subscribe({
                                            userVisibleOnly: true,

                                            applicationServerKey:
                                                key
                                        });


                                await saveSub(sub);


                                $("#notification-permission-banner")
                                    ?.classList.add("d-none");


                                toast(
                                    "Notifications enabled.",
                                    "success"
                                );


                            } catch (err) {

                                console.error(err);

                                toast(
                                    "Notifications could not be enabled.",
                                    "error"
                                );


                            } finally {

                                e.currentTarget.disabled =
                                    false;

                            }

                        }
                    );

            })
            .catch(console.error);

    }


    /* =====================================================
       LOGOUT
       ===================================================== */

    $("#ed-logout-form")
        ?.addEventListener(
            "submit",
            async e => {

                e.preventDefault();

                const form =
                    e.currentTarget;

                const button =
                    $("button", form);


                if (button) {
                    button.disabled = true;
                }


                try {

                    const regs =
                        await navigator.serviceWorker
                            ?.getRegistrations?.() || [];


                    for (const reg of regs) {

                        try {

                            const sub =
                                await reg.pushManager
                                    ?.getSubscription?.();


                            if (sub) {
                                await sub.unsubscribe();
                            }

                        } catch {}

                    }


                } finally {

                    form.submit();

                }

            }
        );

}

})();



/* =========================================================
   GLOBAL APEX PAGE ASSISTANT
   ========================================================= */

(()=>{"use strict";const root=document.getElementById("ed-apex");if(!root)return;const button=document.getElementById("ed-apex-button"),panel=document.getElementById("ed-apex-panel"),closeButton=document.getElementById("ed-apex-close"),form=document.getElementById("ed-apex-form"),input=document.getElementById("ed-apex-input"),sendButton=document.getElementById("ed-apex-send"),responseElement=document.getElementById("ed-apex-response"),statusElement=document.getElementById("ed-apex-status"),pageTitleElement=document.getElementById("ed-apex-page-title"),pageUrlElement=document.getElementById("ed-apex-page-url"),contextToggle=document.getElementById("ed-apex-context-toggle");if(!button||!panel||!closeButton||!form||!input||!sendButton)return;let contextEnabled=true,streaming=false,markdownBuffer="",browserErrors=[];function renderMarkdown(text){if(!window.marked||!window.DOMPurify){responseElement.textContent=text;return}const html=marked.parse(text||"",{gfm:true,breaks:true});responseElement.innerHTML=DOMPurify.sanitize(html,{USE_PROFILES:{html:true}});responseElement.querySelectorAll("table").forEach(table=>{if(table.parentElement.classList.contains("ed-apex-table-wrap"))return;const wrapper=document.createElement("div");wrapper.className="ed-apex-table-wrap";table.parentNode.insertBefore(wrapper,table);wrapper.appendChild(table)});responseElement.scrollTop=responseElement.scrollHeight}function getVisiblePageText(){const clone=document.body.cloneNode(true);clone.querySelectorAll(["script","style","noscript","template","input[type=password]","input[type=hidden]","textarea","[data-apex-ignore]"].join(",")).forEach(e=>e.remove());return(clone.innerText||"").replace(/\s+/g," ").trim().slice(0,12000)}function getSelectedText(){try{return window.getSelection()?.toString().trim().slice(0,6000)||""}catch{return""}}function getSelectedElementInfo(){const selection=window.getSelection();if(!selection||!selection.rangeCount)return{};let node=selection.getRangeAt(0).commonAncestorContainer;if(node.nodeType!==Node.ELEMENT_NODE)node=node.parentElement;if(!node||node.matches?.("input,textarea,select,[type=password]"))return{};return{tag:node.tagName||"",text:(node.innerText||node.textContent||"").replace(/\s+/g," ").trim().slice(0,2000),ariaLabel:node.getAttribute?.("aria-label")||"",role:node.getAttribute?.("role")||""}}function collectContext(){return{title:document.title.slice(0,300),url:window.location.pathname.slice(0,500),selectedText:getSelectedText(),element:getSelectedElementInfo(),errors:browserErrors.slice(-10),visibleText:contextEnabled?getVisiblePageText():""}}function setOpen(open){root.classList.toggle("open",open);button.setAttribute("aria-expanded",String(open));panel.setAttribute("aria-hidden",String(!open));if(open)setTimeout(()=>input.focus(),120)}function setStatus(text){statusElement.textContent=text||""}function clearResponse(){markdownBuffer="";responseElement.innerHTML=""}function appendText(text){markdownBuffer+=text;renderMarkdown(markdownBuffer)}function setLoading(loading){streaming=loading;sendButton.disabled=loading;input.disabled=loading;document.querySelectorAll(".ed-apex-action").forEach(a=>a.disabled=loading);sendButton.innerHTML=loading?'<i class="fa-solid fa-stop"></i>':'<i class="fa-solid fa-arrow-up"></i>'}function showError(message){clearResponse();responseElement.textContent=message;setStatus("Apex encountered an error.")}async function askApex(question){if(streaming)return;question=String(question||"").trim();if(!question)return;clearResponse();setStatus("Apex is looking at the page...");setLoading(true);try{const response=await fetch("/ai/context/",{method:"POST",headers:{"Content-Type":"application/json","X-CSRFToken":window.ED_CONFIG?.csrfToken||"","X-Requested-With":"XMLHttpRequest"},credentials:"same-origin",body:JSON.stringify({question,context:collectContext()})});const data=await response.json();if(!response.ok||!data.success)throw new Error(data.error||"Unable to contact Apex.");if(!data.stream_url)throw new Error("Apex did not provide a stream.");setStatus("Apex is thinking...");await streamResponse(data.stream_url);setStatus("")}catch(error){console.error("Apex error:",error);showError(error.message||"Something went wrong.")}finally{setLoading(false)}}async function streamResponse(streamUrl){const response=await fetch(streamUrl,{method:"GET",credentials:"omit"});if(!response.ok)throw new Error(`Apex stream failed (${response.status}).`);if(!response.body)throw new Error("Streaming is not supported by this browser.");const reader=response.body.getReader(),decoder=new TextDecoder();let buffer="";while(true){const{value,done}=await reader.read();if(done)break;buffer+=decoder.decode(value,{stream:true});const events=buffer.split("\n\n");buffer=events.pop()||"";for(const event of events){for(const line of event.split("\n")){if(!line.startsWith("data:"))continue;const payload=line.slice(5).trim();if(!payload)continue;if(payload==="[DONE]")return;try{const data=JSON.parse(payload);if(data.content)appendText(data.content);if(data.error)throw new Error(data.error)}catch(error){if(error instanceof SyntaxError)continue;throw error}}}}}button.addEventListener("click",()=>setOpen(!root.classList.contains("open")));closeButton.addEventListener("click",()=>setOpen(false));document.addEventListener("keydown",event=>{if(event.key==="Escape"&&root.classList.contains("open"))setOpen(false)});contextToggle.addEventListener("click",()=>{contextEnabled=!contextEnabled;contextToggle.classList.toggle("active",contextEnabled);contextToggle.innerHTML=contextEnabled?'<i class="fa-solid fa-eye"></i>':'<i class="fa-solid fa-eye-slash"></i>';pageUrlElement.textContent=contextEnabled?"Page context enabled":"Page context disabled"});form.addEventListener("submit",async event=>{event.preventDefault();if(streaming)return;const question=input.value.trim();if(!question)return;input.value="";await askApex(question)});input.addEventListener("keydown",event=>{if(event.key==="Enter"&&!event.shiftKey){event.preventDefault();form.requestSubmit()}});document.querySelectorAll("[data-apex-action]").forEach(action=>{action.addEventListener("click",async()=>{const type=action.dataset.apexAction,selected=getSelectedText();if(type==="explain-page")return askApex("Explain this page to me. Tell me what the page is for, what the important sections do, and what I can do here.");if(type==="selected-text"){if(!selected){setStatus("Select some text on the page first.");input.focus();return}return askApex("Explain the text I selected. Give me the relevant context from this page if useful.")}if(type==="find-error")return askApex("Look for a problem or error on this page. Check the page context and any browser errors available to you. If you don't see an actual problem, say so rather than inventing one.")})});window.addEventListener("error",event=>{browserErrors.push({type:"javascript",message:String(event.message||"").slice(0,2000),source:String(event.filename||"").slice(0,500),line:event.lineno||null,column:event.colno||null});if(browserErrors.length>20)browserErrors.shift()});window.addEventListener("unhandledrejection",event=>{browserErrors.push({type:"unhandledrejection",message:String(event.reason?.message||event.reason||"").slice(0,2000),source:"",line:null,column:null});if(browserErrors.length>20)browserErrors.shift()});pageTitleElement.textContent=document.title||"This page";pageUrlElement.textContent="Page context enabled"})();
