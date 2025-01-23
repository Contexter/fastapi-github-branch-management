from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from github import Github
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize router
router = APIRouter(
    prefix="/repos/{owner}/{repo}",
    tags=["Branch Management"],
)

# Dependency to get the GitHub client
def get_github_client():
    token = os.getenv("GH_PAT")
    if not token:
        raise HTTPException(status_code=500, detail="GitHub Personal Access Token (GH_PAT) not configured.")
    return Github(token)

# Models
class Branch(BaseModel):
    name: str
    sha: str  # Include SHA in branch response

class CreateBranchRequest(BaseModel):
    ref: str
    sha: str

# Routes
@router.get(
    "/branches",
    response_model=List[Branch],
    operation_id="listBranches",
    summary="List Branches",
    description="Retrieves a list of branches in the specified repository."
)
async def list_branches(owner: str, repo: str, client=Depends(get_github_client)):
    try:
        repository = client.get_repo(f"{owner}/{repo}")
        branches = repository.get_branches()
        return [{"name": branch.name, "sha": branch.commit.sha} for branch in branches]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving branches: {str(e)}")

@router.get(
    "/branches/{branch}",
    response_model=Branch,
    operation_id="getBranch",
    summary="Get Branch Details",
    description="Retrieves details of a specific branch."
)
async def get_branch(owner: str, repo: str, branch: str, client=Depends(get_github_client)):
    try:
        repository = client.get_repo(f"{owner}/{repo}")
        branch_data = repository.get_branch(branch)
        return {"name": branch_data.name, "sha": branch_data.commit.sha}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Branch not found: {str(e)}")

@router.post(
    "/git/refs",
    operation_id="createBranch",
    summary="Create Branch (via refs)",
    description="Creates a new branch in the specified repository using refs."
)
async def create_branch(owner: str, repo: str, payload: CreateBranchRequest, client=Depends(get_github_client)):
    try:
        repository = client.get_repo(f"{owner}/{repo}")
        ref = f"refs/heads/{payload.ref}"
        repository.create_git_ref(ref=ref, sha=payload.sha)
        return {"detail": "Branch created successfully."}
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Error creating branch: {str(e)}")

@router.delete(
    "/git/refs/heads/{ref}",
    operation_id="deleteBranch",
    summary="Delete Branch (via refs)",
    description="Deletes a specific branch reference."
)
async def delete_branch(owner: str, repo: str, ref: str, client=Depends(get_github_client)):
    try:
        repository = client.get_repo(f"{owner}/{repo}")
        git_ref = repository.get_git_ref(f"heads/{ref}")
        git_ref.delete()
        return {"detail": "Branch deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Branch not found: {str(e)}")
