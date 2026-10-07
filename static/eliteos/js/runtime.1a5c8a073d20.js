window.EliteRuntime = {

    root: null,

    init(root) {
        this.root = root;
    },


    async renderFile(path) {

        const source =
            EliteFS.read(path);

        return this.render(source);
    },


    async render(source) {

        const template =
            document.createElement(
                "template"
            );

        template.innerHTML =
            source.trim();

        const fragment =
            template.content.cloneNode(
                true
            );

        await this.processNode(
            fragment
        );

        return fragment;
    },


    async processNode(node) {

        const children =
            Array.from(
                node.childNodes
            );

        for (
            const child of children
        ) {

            if (
                child.nodeType ===
                Node.ELEMENT_NODE
            ) {

                await this.processElement(
                    child
                );
            }
        }
    },


    async processElement(element) {

        const tag =
            element.tagName
                .toLowerCase();


        /*
         * IMPORT
         */

        if (
            tag ===
            "elite-import"
        ) {

            const src =
                element.getAttribute(
                    "src"
                );

            const fragment =
                await this.renderFile(
                    src
                );

            element.replaceWith(
                fragment
            );

            return;
        }


        /*
         * BUTTON
         */

        if (
            tag ===
            "elite-button"
        ) {

            const button =
                document.createElement(
                    "button"
                );

            button.className =
                "elite-button";

            button.innerHTML =
                element.innerHTML;

            const action =
                element.getAttribute(
                    "action"
                );

            if (action) {

                button.addEventListener(
                    "click",
                    () => {
                        EliteKernel.action(
                            action
                        );
                    }
                );
            }

            element.replaceWith(
                button
            );

            return;
        }


        /*
         * APP CARD
         */

        if (
            tag ===
            "elite-app-card"
        ) {

            const card =
                document.createElement(
                    "button"
                );

            card.className =
                "elite-app-card";

            const icon =
                element.getAttribute(
                    "icon"
                ) || "📦";

            const title =
                element.getAttribute(
                    "title"
                ) || "Application";

            const description =
                element.getAttribute(
                    "description"
                ) || "";

            card.innerHTML = `
                <div class="app-card-icon">
                    ${this.escapeHTML(icon)}
                </div>

                <div class="app-card-body">

                    <strong>
                        ${this.escapeHTML(title)}
                    </strong>

                    <span>
                        ${this.escapeHTML(description)}
                    </span>

                </div>
            `;

            const action =
                element.getAttribute(
                    "action"
                );

            if (action) {

                card.addEventListener(
                    "click",
                    () =>
                        EliteKernel.action(
                            action
                        )
                );
            }

            element.replaceWith(
                card
            );

            return;
        }


        /*
         * BASIC COMPONENTS
         */

        const classes = {

            "elite-desktop":
                "elite-desktop",

            "elite-panel":
                "elite-panel",

            "elite-content":
                "elite-content",

            "elite-section":
                "elite-section",

            "elite-row":
                "elite-row",

            "elite-brand":
                "elite-brand",

            "elite-user":
                "elite-user",

            "elite-clock":
                "elite-clock",

            "elite-welcome":
                "elite-welcome",

            "elite-launcher":
                "elite-launcher",

            "elite-taskbar":
                "elite-taskbar",

            "elite-heading":
                "elite-heading",

            "elite-screen":
                "elite-screen",

            "elite-app":
                "elite-app",

            "elite-window":
                "elite-window",

            "elite-window-header":
                "elite-window-header",
        };


        if (
            classes[tag]
        ) {

            element.classList.add(
                classes[tag]
            );
        }


        /*
         * TITLE
         */

        if (
            tag ===
            "elite-title"
        ) {

            element.classList.add(
                "elite-title"
            );
        }


        /*
         * TEXT
         */

        if (
            tag ===
            "elite-text"
        ) {

            element.classList.add(
                "elite-text"
            );
        }


        /*
         * CLOCK
         */

        if (
            tag ===
            "elite-clock"
        ) {

            element.classList.add(
                "elite-clock"
            );

            const update = () => {

                element.textContent =
                    new Date()
                        .toLocaleTimeString(
                            [],
                            {
                                hour:
                                    "2-digit",

                                minute:
                                    "2-digit",
                            }
                        );
            };

            update();

            setInterval(
                update,
                1000
            );
        }


        /*
         * CALCULATOR
         */

        if (
            tag ===
            "elite-calculator"
        ) {

            this.createCalculator(
                element
            );

            return;
        }


        /*
         * FILE BROWSER
         */

        if (
            tag ===
            "elite-file-browser"
        ) {

            this.createFileBrowser(
                element
            );

            return;
        }


        /*
         * DOCUMENT EDITOR
         */

        if (
            tag ===
            "elite-document-editor"
        ) {

            this.createDocumentEditor(
                element
            );

            return;
        }


        /*
         * RECURSION
         */

        await this.processNode(
            element
        );
    },


    createCalculator(element) {

        element.innerHTML = `
            <div class="calculator">

                <input
                    class="calculator-display"
                    value="0"
                    readonly
                >

                <div class="calculator-grid">

                    ${[
                        "7","8","9","/",
                        "4","5","6","*",
                        "1","2","3","-",
                        "0",".","=","+",
                    ].map(
                        key => `
                            <button
                                data-key="${key}"
                            >
                                ${key}
                            </button>
                        `
                    ).join("")}

                </div>

                <button
                    class="calculator-clear"
                    data-key="C"
                >
                    Clear
                </button>

            </div>
        `;

        const display =
            element.querySelector(
                ".calculator-display"
            );

        let expression = "";

        element
            .querySelectorAll(
                "[data-key]"
            )
            .forEach(button => {

                button.addEventListener(
                    "click",
                    () => {

                        const key =
                            button.dataset.key;

                        if (
                            key === "C"
                        ) {

                            expression = "";
                            display.value = "0";

                            return;
                        }

                        if (
                            key === "="
                        ) {

                            try {

                                /*
                                 * Deliberately limited
                                 * calculator expression.
                                 */

                                if (
                                    !/^[0-9+\-*/.() ]+$/
                                        .test(
                                            expression
                                        )
                                ) {

                                    throw new Error(
                                        "Invalid expression"
                                    );
                                }

                                const result =
                                    Function(
                                        `"use strict"; return (${expression})`
                                    )();

                                expression =
                                    String(result);

                                display.value =
                                    expression;

                            } catch {

                                expression = "";
                                display.value =
                                    "Error";
                            }

                            return;
                        }

                        expression += key;
                        display.value =
                            expression;
                    }
                );
            });
    },


    createFileBrowser(element) {

        const path =
            element.getAttribute(
                "path"
            ) || "/";

        const files =
            EliteFS.list(path);

        element.innerHTML = `
            <div class="file-browser">

                ${files.length
                    ? files.map(
                        file => `

                            <button
                                class="file-browser-item"
                            >

                                <span>
                                    ${
                                        file.type ===
                                        "directory"
                                            ? "📁"
                                            : "📄"
                                    }
                                </span>

                                <span>
                                    ${
                                        this.escapeHTML(
                                            file.path
                                        )
                                    }
                                </span>

                            </button>
                        `
                    ).join("")

                    : `
                        <div class="empty-state">
                            This folder is empty.
                        </div>
                    `
                }

            </div>
        `;
    },


    createDocumentEditor(element) {

        element.innerHTML = `

            <div class="document-editor">

                <div class="editor-toolbar">

                    <button
                        data-command="bold"
                    >
                        <strong>B</strong>
                    </button>

                    <button
                        data-command="italic"
                    >
                        <em>I</em>
                    </button>

                    <button
                        data-command="underline"
                    >
                        <u>U</u>
                    </button>

                </div>

                <div
                    class="document-page"
                    contenteditable="true"
                    spellcheck="true"
                >
                    <h1>
                        Untitled Document
                    </h1>

                    <p>
                        Start writing...
                    </p>
                </div>

                <div class="editor-footer">

                    <span>
                        Document
                    </span>

                    <button
                        class="elite-button"
                        id="save-document"
                    >
                        Save
                    </button>

                </div>

            </div>
        `;

        element
            .querySelectorAll(
                "[data-command]"
            )
            .forEach(button => {

                button.addEventListener(
                    "click",
                    () => {

                        document.execCommand(
                            button.dataset.command
                        );
                    }
                );
            });


        element
            .querySelector(
                "#save-document"
            )
            .addEventListener(
                "click",
                async () => {

                    const content =
                        element
                            .querySelector(
                                ".document-page"
                            )
                            .innerHTML;

                    const path =
                        `/home/${EliteKernel.username}/Documents/Untitled.html`;

                    EliteFS.write(
                        path,
                        content
                    );

                    try {

                        await EliteFS.save();

                        alert(
                            "Document saved."
                        );

                    } catch (error) {

                        alert(
                            error.message
                        );
                    }
                }
            );
    },


    escapeHTML(value) {

        const div =
            document.createElement(
                "div"
            );

        div.textContent =
            String(value);

        return div.innerHTML;
    },

};