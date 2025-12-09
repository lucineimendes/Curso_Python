// Gerenciamento do Roadmap Visual do Curso

class CourseRoadmap {
    constructor(courseId, containerId) {
        this.courseId = courseId;
        this.container = document.getElementById(containerId);
        this.progress = { lessons: {}, exercises: {} };
        this.loadProgressFromServer();
    }

    async loadProgressFromServer() {
        try {
            const response = await fetch(`/api/progress/course/${this.courseId}`);
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.progress) {
                    this.progress = {
                        lessons: data.progress.lessons || {},
                        exercises: data.progress.exercises || {},
                    };
                    // Também salvar no localStorage como backup
                    this.saveProgress();
                    // Atualizar visual se já foi renderizado
                    if (this.container && this.container.innerHTML) {
                        this.updateVisual();
                    }
                }
            }
        } catch (error) {
            console.error('Erro ao carregar progresso do servidor:', error);
            // Fallback para localStorage
            this.loadProgressFromLocalStorage();
        }
    }

    loadProgressFromLocalStorage() {
        const stored = localStorage.getItem(`progress_${this.courseId}`);
        if (stored) {
            this.progress = JSON.parse(stored);
        }
    }

    saveProgress() {
        localStorage.setItem(`progress_${this.courseId}`, JSON.stringify(this.progress));
    }

    markLessonComplete(lessonId) {
        this.progress.lessons[lessonId] = {
            completed: true,
            completedAt: new Date().toISOString(),
        };
        this.saveProgress();
        this.updateVisual();
        this.syncWithServer(lessonId, 'lesson');

        // Verificar novas conquistas
        this.checkAchievements();
    }

    markExerciseComplete(exerciseId) {
        this.progress.exercises[exerciseId] = {
            completed: true,
            completedAt: new Date().toISOString(),
        };
        this.saveProgress();
        this.updateVisual();
        this.syncWithServer(exerciseId, 'exercise');

        // Verificar novas conquistas
        this.checkAchievements();
    }

    syncWithServer(itemId, type) {
        const endpoint =
            type === 'lesson'
                ? '/api/progress/lesson'
                : '/api/progress/exercise';

        fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                course_id: this.courseId,
                [type + '_id']: itemId,
            }),
        })
            .then(response => response.json())
            .then(data => {
                console.log('Progresso sincronizado:', data);
            })
            .catch(error => {
                console.error('Erro ao sincronizar progresso:', error);
            });
    }

    calculateStatistics(lessons, exercises) {
        const completedLessons = Object.keys(this.progress.lessons).filter(
            id => this.progress.lessons[id].completed
        ).length;

        const completedExercises = Object.keys(this.progress.exercises).filter(
            id => this.progress.exercises[id].completed
        ).length;

        const totalLessons = lessons.length;
        const totalExercises = exercises.length;

        const lessonsPercentage =
            totalLessons > 0 ? (completedLessons / totalLessons) * 100 : 0;
        const exercisesPercentage =
            totalExercises > 0 ? (completedExercises / totalExercises) * 100 : 0;
        const overallPercentage = (lessonsPercentage + exercisesPercentage) / 2;

        return {
            completedLessons,
            totalLessons,
            lessonsPercentage: Math.round(lessonsPercentage),
            completedExercises,
            totalExercises,
            exercisesPercentage: Math.round(exercisesPercentage),
            overallPercentage: Math.round(overallPercentage),
        };
    }

    render(lessons, exercises) {
        if (!this.container) return;

        const stats = this.calculateStatistics(lessons, exercises);

        // Criar HTML do roadmap
        const html = `
            <div class="roadmap-container">
                <div class="roadmap-header">
                    <h3>Progresso do Curso</h3>
                    <div class="progress-stats">
                        <div class="stat-item">
                            <span class="stat-label">Progresso Geral</span>
                            <span class="stat-value">${stats.overallPercentage}%</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Lições</span>
                            <span class="stat-value">${stats.completedLessons}/${stats.totalLessons}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Exercícios</span>
                            <span class="stat-value">${stats.completedExercises}/${stats.totalExercises}</span>
                        </div>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar" style="width: ${stats.overallPercentage}%"></div>
                    </div>
                </div>

                <div class="roadmap-content">
                    ${this.renderLessonsMap(lessons, exercises)}
                </div>
            </div>
        `;

        this.container.innerHTML = html;
        this.attachEventListeners();
    }

    renderLessonsMap(lessons, exercises) {
        return lessons
            .map((lesson, index) => {
                const isCompleted = this.progress.lessons[lesson.id]?.completed;
                const lessonExercises = exercises.filter(
                    ex => ex.lesson_id === lesson.id
                );

                const completedExercises = lessonExercises.filter(
                    ex => this.progress.exercises[ex.id]?.completed
                ).length;

                const exerciseProgress =
                    lessonExercises.length > 0
                        ? Math.round(
                              (completedExercises / lessonExercises.length) * 100
                          )
                        : 0;

                return `
                    <div class="roadmap-node ${isCompleted ? 'completed' : ''}" data-lesson-id="${lesson.id}">
                        <div class="node-connector ${index > 0 ? 'visible' : ''}"></div>
                        <div class="node-circle">
                            <span class="node-number">${index + 1}</span>
                            ${isCompleted ? '<span class="node-check">✓</span>' : ''}
                        </div>
                        <div class="node-content">
                            <h4 class="node-title">${lesson.title}</h4>
                            <p class="node-description">${lesson.description || ''}</p>
                            ${
                                lessonExercises.length > 0
                                    ? `
                                <div class="node-exercises">
                                    <span class="exercises-label">Exercícios: ${completedExercises}/${lessonExercises.length}</span>
                                    <div class="mini-progress-bar">
                                        <div class="mini-progress-fill" style="width: ${exerciseProgress}%"></div>
                                    </div>
                                </div>
                                <div class="exercise-list">
                                    ${lessonExercises
                                        .map(
                                            ex => `
                                        <div class="exercise-item ${this.progress.exercises[ex.id]?.completed ? 'completed' : ''}"
                                             data-exercise-id="${ex.id}">
                                            <span class="exercise-icon">${this.progress.exercises[ex.id]?.completed ? '✓' : '○'}</span>
                                            <span class="exercise-name">${ex.title}</span>
                                        </div>
                                    `
                                        )
                                        .join('')}
                                </div>
                            `
                                    : ''
                            }
                            <a href="/courses/${this.courseId}/lessons/${lesson.id}" class="node-link">
                                ${isCompleted ? 'Revisar Lição' : 'Iniciar Lição'} →
                            </a>
                        </div>
                    </div>
                `;
            })
            .join('');
    }

    attachEventListeners() {
        // Adicionar listeners para interações futuras
        const nodes = this.container.querySelectorAll('.roadmap-node');
        nodes.forEach(node => {
            node.addEventListener('click', e => {
                if (!e.target.classList.contains('node-link')) {
                    node.classList.toggle('expanded');
                }
            });
        });
    }

    updateVisual() {
        // Recarregar o roadmap com dados atualizados
        if (typeof courseData !== 'undefined' && courseData.lessons && courseData.exercises) {
            this.render(courseData.lessons, courseData.exercises);
        }
    }

    async checkAchievements() {
        try {
            const response = await fetch('/api/achievements/check', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: 'default'
                }),
            });

            if (response.ok) {
                const data = await response.json();

                if (data.success && data.newly_unlocked && data.newly_unlocked.length > 0) {
                    console.log('Novas conquistas desbloqueadas:', data.newly_unlocked);

                    // Exibir notificações para cada conquista
                    if (window.achievementNotifier) {
                        data.newly_unlocked.forEach(achievement => {
                            window.achievementNotifier.show(achievement);
                        });
                    }

                    // Atualizar contador de badges
                    if (window.badgeCounter) {
                        window.badgeCounter.forceUpdate();
                    }
                }
            }
        } catch (error) {
            console.error('Erro ao verificar conquistas:', error);
        }
    }
}

// Função auxiliar para recarregar o roadmap
function reloadRoadmap() {
    if (window.courseRoadmap) {
        window.courseRoadmap.loadProgressFromServer();
    }
}

// Inicializar roadmap quando a página carregar
document.addEventListener('DOMContentLoaded', async function () {
    const roadmapContainer = document.getElementById('course-roadmap');
    if (roadmapContainer && typeof courseData !== 'undefined') {
        const roadmap = new CourseRoadmap(
            courseData.courseId,
            'course-roadmap'
        );

        // Tornar disponível globalmente para outras funções
        window.courseRoadmap = roadmap;

        // Aguardar carregamento do progresso e então renderizar
        await roadmap.loadProgressFromServer();
        roadmap.render(courseData.lessons, courseData.exercises);
    }
});
