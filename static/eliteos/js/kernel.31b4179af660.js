window.EliteKernel = {

    root: null,

    username: "",


    async init() {

        this.root =
            document.getElementById(
                "eliteos-app"
            );

        EliteRuntime.init(
            this.root
        );

        EliteRecovery.init();

        await this.boot();
    },


    showScreen(id) {

        document
            .querySelectorAll(".screen")
            .forEach(
                screen =>
                    screen.classList.remove(
                        "active"
                    )
            );

        document
            .getElementById(id)
            .classList.add(
                "active"
            );
    },


    async boot() {

        try {

            this.showScreen(
                "bios-screen"
            );

            const config =
                await EliteBIOS.boot();


            await fetch(
                window
                    .ELITEOS_CONFIG
                    .bootUrl,

                {
                    method: "POST",

                    credentials:
                        "same-origin",

                    headers: {
                        "X-CSRFToken":
                            window
                            .ELITEOS_CONFIG
                            .csrfToken,
                    },
                }
            );


            this.showScreen(
                "boot-screen"
            );


            await new Promise(
                resolve =>
                    setTimeout(
                        resolve,
                        300
                    )
            );


            this.showScreen(
                "os-screen"
            );


            await EliteRuntime.mount(
                config.boot
            );

        } catch (error) {

            EliteRecovery.show(
                error
            );
        }
    },


    async openApp(appId) {

        const path =
            `/apps/${appId}/app.ehtml`;

        if (
            !EliteFS.exists(path)
        ) {

            throw new Error(
                `Application not found: ${appId}`
            );
        }

        this.showScreen(
            "os-screen"
        );

        await EliteRuntime.mount(
            path
        );
    },


    action(action) {

        console.log(
            "EliteOS action:",
            action
        );


        const apps = {
            "open-appstore":
                "appstore",

            "open-files":
                "files",

            "open-calculator":
                "calculator",

            "open-documents":
                "documents",

            "open-settings":
                "settings",
        };


        if (
            apps[action]
        ) {

            this.openApp(
                apps[action]
            );

            return;
        }


        if (
            action ===
            "show-system"
        ) {

            this.showSystemInfo();

            return;
        }


        if (
            action ===
            "toggle-theme"
        ) {

            document.body.classList.toggle(
                "light-theme"
            );

            return;
        }


        if (
            action ===
            "reboot"
        ) {

            this.boot();

            return;
        }


        if (
            action ===
            "recovery"
        ) {

            this.showScreen(
                "recovery-screen"
            );

            return;
        }


        console.warn(
            "Unknown EliteOS action:",
            action
        );
    },


    showSystemInfo() {

        const info =
            EliteFS.info();

        this.root.innerHTML = `

            <div class="elite-window">

                <div class="elite-window-header">

                    <strong>
                        System Information
                    </strong>

                    <button
                        onclick="
                            EliteKernel.boot()
                        "
                    >
                        Desktop
                    </button>

                </div>

                <div class="system-info">

                    <div class="info-card">

                        <span>
                            Filesystem
                        </span>

                        <strong>
                            ${info.format}
                        </strong>

                    </div>

                    <div class="info-card">

                        <span>
                            Compressed Usage
                        </span>

                        <strong>
                            ${info.compressedSize}
                            /
                            ${info.maxSize}
                            bytes
                        </strong>

                    </div>

                    <div class="info-card">

                        <span>
                            Usage
                        </span>

                        <strong>
                            ${info.percent.toFixed(1)}%
                        </strong>

                    </div>

                </div>

            </div>
        `;
    },

};


document.addEventListener(
    "DOMContentLoaded",
    () => EliteKernel.init()
);