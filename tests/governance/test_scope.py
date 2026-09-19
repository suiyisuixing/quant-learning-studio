"""Synthetic identities only. No impersonation or external account operations."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from check_pr_scope import ScopeError,evaluate,validate_policy,within
from publication_scan import scan_blob,scan_name


class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.sha='a'*40
        self.user={'login':'fixture-member','id':900000002}
        self.policy={'version':1,'owner':{'login':'fixture-owner','id':900000001},'members':[{'role':'fixture-member','name':'Synthetic test fixture','login':self.user['login'],'id':self.user['id'],'identity_status':'VERIFIED','plan_path':'team/fixture-member/PLAN.md','module_paths':['materials/factors/'],'implementation_approval':{'approved_by':900000001,'plan_blob_sha':self.sha,'approved_paths':['materials/factors/']}}]}

    def files(self,path,status='modified',previous=None):
        f={'filename':path,'status':status}
        if previous: f['previous_filename']=previous
        return [f]

    def check(self,files=None,author=None,sha=None,count=None):
        files=files or self.files('materials/factors/card.md')
        return evaluate(self.policy,author or self.user,files,len(files) if count is None else count,self.sha if sha is None else sha)

    def test_approved_scope_passes(self): self.assertIn('exact approved',self.check())
    def test_unknown_author_fails(self):
        with self.assertRaises(ScopeError): self.check(author={'id':1,'login':'unknown-fixture'})
    def test_login_without_numeric_identity_fails(self):
        with self.assertRaises(ScopeError): self.check(author={'id':3,'login':self.user['login']})
    def test_numeric_identity_with_wrong_login_fails(self):
        with self.assertRaises(ScopeError): self.check(author={'id':self.user['id'],'login':'renamed-fixture'})
    def test_pending_member_fails(self):
        m=self.policy['members'][0];m.update(id=None,login=None,identity_status='PENDING',implementation_approval=None)
        with self.assertRaises(ScopeError): self.check()
    def test_plan_only_before_approval_passes(self):
        self.policy['members'][0]['implementation_approval']=None
        self.assertIn('PLAN-only',self.check(self.files('team/fixture-member/PLAN.md')))
    def test_unapproved_implementation_fails(self):
        self.policy['members'][0]['implementation_approval']=None
        with self.assertRaises(ScopeError): self.check()
    def test_other_person_plan_fails(self):
        with self.assertRaises(ScopeError): self.check(self.files('team/another-member/PLAN.md'))
    def test_scope_escape_fails(self):
        with self.assertRaises(ScopeError): self.check(self.files('materials/risk/card.md'))
    def test_directory_prefix_collision_fails(self):
        with self.assertRaises(ScopeError): self.check(self.files('materials/factors-private/card.md'))
    def test_policy_self_change_fails(self):
        with self.assertRaises(ScopeError): self.check(self.files('.github/team-policy.json'))
    def test_workflow_change_fails(self):
        with self.assertRaises(ScopeError): self.check(self.files('.github/workflows/governance.yml'))
    def test_checker_change_fails(self):
        with self.assertRaises(ScopeError): self.check(self.files('scripts/check_pr_scope.py'))
    def test_rename_from_outside_fails(self):
        with self.assertRaises(ScopeError): self.check(self.files('materials/factors/card.md','renamed','materials/risk/card.md'))
    def test_rename_to_outside_fails(self):
        with self.assertRaises(ScopeError): self.check(self.files('materials/risk/card.md','renamed','materials/factors/card.md'))
    def test_rename_within_scope_passes(self): self.check(self.files('materials/factors/b.md','renamed','materials/factors/a.md'))
    def test_missing_rename_source_fails(self):
        with self.assertRaises(ScopeError): self.check(self.files('materials/factors/b.md','renamed'))
    def test_plan_edit_mixed_with_implementation_fails(self):
        with self.assertRaises(ScopeError): self.check(self.files('team/fixture-member/PLAN.md')+self.files('materials/factors/a.md'))
    def test_stale_plan_approval_fails(self):
        with self.assertRaises(ScopeError): self.check(sha='b'*40)
    def test_incomplete_file_list_fails(self):
        with self.assertRaises(ScopeError): self.check(count=2)
    def test_duplicate_file_list_fails(self):
        with self.assertRaises(ScopeError): self.check(self.files('materials/factors/a.md')*2)
    def test_owner_passes_shared_file_without_self_review(self): self.check(self.files('.github/CODEOWNERS'),self.policy['owner'])
    def test_traversal_fails(self):
        for path in ['../secret','/etc/passwd','materials/factors/../risk/a.md','materials/factors\\..\\risk','materials//factors/a.md']:
            with self.subTest(path=path),self.assertRaises(ScopeError): self.check(self.files(path))
    def test_nonowner_approval_fails(self):
        self.policy['members'][0]['implementation_approval']['approved_by']=self.user['id']
        with self.assertRaises(ScopeError): self.check()
    def test_approval_outside_role_module_fails(self):
        self.policy['members'][0]['implementation_approval']['approved_paths']=['content/cases/']
        with self.assertRaises(ScopeError): self.check()
    def test_duplicate_identity_fails(self):
        m=copy.deepcopy(self.policy['members'][0]);m.update(role='another-member',plan_path='team/another-member/PLAN.md');self.policy['members'].append(m)
        with self.assertRaises(ScopeError): validate_policy(self.policy)
    def test_pending_identity_cannot_include_approval(self):
        self.policy['members'][0]['identity_status']='PENDING'
        with self.assertRaises(ScopeError): validate_policy(self.policy)
    def test_credentials_detected_without_printing(self):
        self.assertTrue(scan_blob(('gh'+'p_'+'A'*40).encode()))
        self.assertTrue(scan_blob(('sk-'+'B'*32).encode()))
    def test_restricted_files_detected(self):
        for path in ['private/notes.md','research/paper.pdf','app.db','.env.local','data/trades.csv']:
            self.assertTrue(scan_name(path),path)
    def test_example_environment_name_allowed(self): self.assertFalse(scan_name('.env.example'))


if __name__=='__main__': unittest.main()
