const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function handleResponse(res) {
  if (!res.ok) {
    let errMsg = `Server error: ${res.status}`;
    try {
      const errBody = await res.json();
      if (errBody.detail) errMsg = errBody.detail;
    } catch (e) {}
    throw new Error(errMsg);
  }
  return res.json();
}

export async function checkReadiness(policyFile, claimFiles) {
  const formData = new FormData();
  formData.append('policy', policyFile);
  for (const file of claimFiles) {
    formData.append('claims', file);
  }

  const res = await fetch(`${API_BASE}/readiness/pipeline`, {
    method: 'POST',
    body: formData,
  });

  return handleResponse(res);
}

export async function checkAdjudication(policyFile, rejectionFile) {
  const formData = new FormData();
  formData.append('policy', policyFile);
  formData.append('rejection', rejectionFile);

  const res = await fetch(`${API_BASE}/adjudication/pipeline`, {
    method: 'POST',
    body: formData,
  });

  return handleResponse(res);
}

export async function runEval() {
  const res = await fetch(`${API_BASE}/eval/run`, {
    method: 'POST',
  });

  return handleResponse(res);
}
