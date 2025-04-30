document.getElementById('resume-upload').addEventListener('change', handleFileUpload);
document.getElementById('job-description').addEventListener('input', updateMatchButton);
document.getElementById('match-btn').addEventListener('click', analyzeMatch);

let resumeText = '';

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            resumeText = e.target.result;
            document.getElementById('upload-status').textContent = 'File uploaded successfully';
            updateMatchButton();
        };
        reader.readAsText(file);
    }
}

function updateMatchButton() {
    const jobDescription = document.getElementById('job-description').value.trim();
    const matchButton = document.getElementById('match-btn');
    matchButton.disabled = !resumeText || !jobDescription;
}

function analyzeMatch() {
    const jobDescription = document.getElementById('job-description').value.trim();
    const skills = ['javascript', 'python', 'react', 'node', 'typescript', 'java', 'sql', 'aws'];
    const matchedSkills = skills.filter(skill => resumeText.toLowerCase().includes(skill) && jobDescription.toLowerCase().includes(skill));
    const unmatchedSkills = skills.filter(skill => !matchedSkills.includes(skill));

    const matchScore = Math.round((matchedSkills.length / skills.length) * 100);
    document.getElementById('match-score').textContent = `Match Score: ${matchScore}%`;

    document.getElementById('matched-skills').innerHTML = matchedSkills.map(skill => `<li>${skill}</li>`).join('');
    document.getElementById('unmatched-skills').innerHTML = unmatchedSkills.map(skill => `<li>${skill}</li>`).join('');

    // Example job role and experience requirements
    document.getElementById('job-role').textContent = 'Job Role: Full Stack Developer';
    document.getElementById('experience-required').textContent = 'Experience Required: 3+ years in software development';

    document.getElementById('results-section').classList.remove('hidden');
}
