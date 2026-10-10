// ============================================================
// ماژول پرسشنامه - ورودی اصلی
// ============================================================

// ===== صادرات از ماژول‌های مختلف =====
export {
    buildQuestions,
    buildMcqQuestions,
    buildOpenQuestions,
    loadSavedAnswers
} from './builder.js';

export {
    validateAndGo,
    goToPage,
    getCurrentPageId,
    getMcqProgress,
    updateContinueBadge
} from './validator.js';

export {
    selectOption,
    saveCurrentAnswers,
    startQuestionnaire,
    submitAll,
    resetApp
} from './submitter.js';

export {
    startRecording,
    stopRecording,
    getAudioBlob,
    loadAllAudioFiles
} from './recording.js';

// ============================================================
// صادرات به window برای استفاده در HTML و main.js
// ============================================================

import {
    buildQuestions,
    buildMcqQuestions,
    buildOpenQuestions,
    loadSavedAnswers
} from './builder.js';

import {
    validateAndGo,
    goToPage,
    getCurrentPageId,
    getMcqProgress,
    updateContinueBadge
} from './validator.js';

import {
    selectOption,
    saveCurrentAnswers,
    startQuestionnaire,
    submitAll,
    resetApp
} from './submitter.js';

import {
    startRecording,
    stopRecording,
    getAudioBlob,
    loadAllAudioFiles
} from './recording.js';
import { updateProgress } from './validator.js';
window.updateProgress = updateProgress;
// ===== الصاق به window برای دسترسی در HTML =====
window.buildQuestions = buildQuestions;
window.buildMcqQuestions = buildMcqQuestions;
window.buildOpenQuestions = buildOpenQuestions;
window.loadSavedAnswers = loadSavedAnswers;

window.validateAndGo = validateAndGo;
window.goToPage = goToPage;
window.getCurrentPageId = getCurrentPageId;
window.getMcqProgress = getMcqProgress;
window.updateContinueBadge = updateContinueBadge;

window.selectOption = selectOption;
window.saveCurrentAnswers = saveCurrentAnswers;
window.startQuestionnaire = startQuestionnaire;
window.submitAll = submitAll;
window.resetApp = resetApp;

window.startRecording = startRecording;
window.stopRecording = stopRecording;
window.getAudioBlob = getAudioBlob;
window.loadAllAudioFiles = loadAllAudioFiles;