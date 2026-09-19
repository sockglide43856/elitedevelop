window.EliteRecovery = {

    show(error) {

        console.error(
            "EliteOS boot failure:",
            error
        );

        EliteKernel.showScreen(
            "recovery-screen"
        );

        document.getElementById(
            "recovery-error"
        ).textContent =
            error.message ||
            "An unknown boot error occurred.";
    },


    init() {

        document
            .getElementById("retry-boot")
            .addEventListener(
                "click",
                () => {

                    EliteKernel.boot();
                }
            );


        document
            .getElementById("safe-mode")
            .addEventListener(
                "click",
                async () => {

                    try {

                        EliteKernel.showScreen(
                            "os-screen"
                        );

                        await EliteRuntime.mount(
                            "/boot/safe.ehtml"
                        );

                    } catch (error) {

                        this.show(error);
                    }
                }
            );


        document
            .getElementById("reset-os")
            .addEventListener(
                "click",
                async () => {

                    if (
                        !confirm(
                            "Reset your EliteOS filesystem?"
                        )
                    ) {
                        return;
                    }

                    await fetch(

                        window.ELITEOS_CONFIG.resetUrl,

                        {
                            method:
                                "POST",

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

                    location.reload();
                }
            );


        document
            .getElementById("exit-os")
            .addEventListener(
                "click",
                () => {

                    window.location.href =
                        window
                        .ELITEOS_CONFIG
                        .homeUrl;
                }
            );
    },

};