workspace "AIContextCraft Architecture" "C4 model for AIContextCraft CLI and supporting flows." {

    model {
        properties {
            "structurizr.groupSeparator" "/"
        }

        developer = person "Developer" "Runs AIContextCraft from local terminal or CI."
        ciRunner = person "CI Runner" "Executes validation and automation jobs."

        targetRepository = softwareSystem "Target Repository" "Codebase scanned and filtered to produce LLM-ready context."
        localClipboard = softwareSystem "System Clipboard" "Receives generated content when clipboard copy is enabled."
        localGit = softwareSystem "Git Repository" "Provides refs and diffs for --git-diff mode."
        outputStorage = softwareSystem "Output Filesystem" "Stores generated context files and logs."

        aiContextCraft = softwareSystem "AIContextCraft" "CLI tool that builds structured context and diff reports for LLM workflows." {
            cliEntrypoint = container "CLI Entrypoint" "Parses CLI flags, resolves config, orchestrates execution mode." "Python (main.py)"
            filteringEngine = container "Filtering and Ignore Engine" "Applies include/exclude filters and hierarchical ignore rules." "Python (FilterManager + IgnoreManager)"
            contextPipeline = container "Context Builder Pipeline" "Scans files, builds tree metadata, processes content, and aggregates sections." "Python (ContextBuilder)"
            formatter = container "Output Formatter" "Renders final output as xml/text/markdown." "Python (formatter.py)"
            diffGenerator = container "Git Diff Reporter" "Builds markdown reports between two Git revisions." "Python (git_manager.py)"
            ioLayer = container "Output and Clipboard Layer" "Writes files/logs and optionally copies result to clipboard." "Filesystem + pyperclip/OSC52"
        }

        developer -> aiContextCraft "Runs commands and reads output"
        ciRunner -> aiContextCraft "Executes automated checks and docs generation"
        aiContextCraft -> targetRepository "Reads files, ignore files, and project structure"
        aiContextCraft -> localGit "Reads refs and computes diff report in git-diff mode"
        aiContextCraft -> outputStorage "Writes generated output and logs"
        aiContextCraft -> localClipboard "Copies generated content when enabled"

        developer -> cliEntrypoint "Invokes main CLI"
        ciRunner -> cliEntrypoint "Invokes automation commands"
        cliEntrypoint -> filteringEngine "Builds filtering strategy"
        cliEntrypoint -> contextPipeline "Triggers standard context mode"
        cliEntrypoint -> diffGenerator "Triggers git-diff mode"
        contextPipeline -> filteringEngine "Queries include/exclude and ignore decisions"
        contextPipeline -> targetRepository "Reads candidate files"
        contextPipeline -> formatter "Builds formatted output body"
        diffGenerator -> localGit "Computes diff report"
        formatter -> ioLayer "Sends formatted content"
        diffGenerator -> ioLayer "Sends diff report"
        ioLayer -> outputStorage "Writes output artifacts"
        ioLayer -> localClipboard "Copies content when allowed"
    }

    views {
        systemContext aiContextCraft "systemContext" {
            include developer ciRunner targetRepository localGit outputStorage localClipboard
            autolayout lr
            title "System Context - AIContextCraft"
        }

        container aiContextCraft "containerView" {
            include developer ciRunner targetRepository localGit outputStorage localClipboard
            include cliEntrypoint filteringEngine contextPipeline formatter diffGenerator ioLayer
            autolayout lr
            title "Container View - AIContextCraft Execution Architecture"
        }

        container aiContextCraft "processingFlowView" {
            include developer cliEntrypoint filteringEngine contextPipeline formatter ioLayer targetRepository outputStorage localClipboard
            autolayout lr
            title "Processing Flow View - Standard Context Mode"
        }

        styles {
            element "Person" {
                shape person
                background #08427b
                color #ffffff
            }

            element "Software System" {
                background #1168bd
                color #ffffff
            }

            element "Container" {
                background #438dd5
                color #ffffff
            }
        }
    }
}
