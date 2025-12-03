let editor;

function initializeExercisePage(courseId, exerciseId) {
    editor = CodeMirror.fromTextArea(document.getElementById("codeEditor"), {
        mode: "python",
        lineNumbers: true,
        theme: "material-darker", // ou outro tema de sua preferência
        indentUnit: 4,
        matchBrackets: true,
        autoCloseBrackets: true,
    });

    const submitButton = document.getElementById("submitCodeBtn");
    if (submitButton) {
        submitButton.addEventListener("click", () => submitCode(courseId, exerciseId));
    }
}

async function submitCode(courseId, exerciseId) {
    const userCode = editor.getValue();
    const outputArea = document.getElementById("outputArea");
    const outputContent = document.getElementById("outputContent");
    const outputDetails = document.getElementById("outputDetails");

    outputArea.style.display = "block";
    outputContent.textContent = "Executando...";
    outputDetails.textContent = "";
    outputArea.className = "output-area"; // Reset class

    try {
        const response = await fetch(`/submit_exercise/${courseId}/${exerciseId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ code: userCode }),
        });

        if (!response.ok) {
            throw new Error(`Erro na requisição: ${response.status} ${response.statusText}`);
        }

        const result = await response.json();

        outputContent.textContent = result.output || "(Nenhuma saída padrão)";
        outputDetails.textContent = result.details || "";

        outputArea.classList.add(result.success ? "success" : "error");

        // Se o exercício foi completado com sucesso, marcar no progresso
        if (result.success) {
            markExerciseComplete(courseId, exerciseId);
        }

    } catch (error) {
        outputContent.textContent = "Erro ao submeter o código.";
        outputDetails.textContent = error.message;
        outputArea.classList.add("error");
    }
}

async function markExerciseComplete(courseId, exerciseId) {
    try {
        const response = await fetch('/api/progress/exercise', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                course_id: courseId,
                exercise_id: exerciseId,
                success: true,
            }),
        });

        if (response.ok) {
            const data = await response.json();
            console.log('Exercício marcado como completo:', data);

            // Atualizar roadmap se estiver disponível
            if (window.courseRoadmap) {
                window.courseRoadmap.markExerciseComplete(exerciseId);
            }
        }
    } catch (error) {
        console.error('Erro ao marcar exercício como completo:', error);
    }
}
