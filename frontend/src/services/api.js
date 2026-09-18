const API_BASE = '';

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

  if (!res.ok) {
    throw new Error(`Server error: ${res.status}`);
  }

  return res.json();
}

export async function checkAdjudication(policyFile, rejectionFile) {
  const formData = new FormData();
  formData.append('policy', policyFile);
  formData.append('rejection', rejectionFile);

  const res = await fetch(`${API_BASE}/adjudication/pipeline`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    throw new Error(`Server error: ${res.status}`);
  }

  return res.json();
}

export async function runEval() {
  const res = await fetch(`${API_BASE}/eval/run`, {
    method: 'POST',
  });

  if (!res.ok) {
    throw new Error(`Server error: ${res.status}`);
  }

  return res.json();
}
