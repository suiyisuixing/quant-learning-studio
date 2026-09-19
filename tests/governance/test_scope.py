"""Synthetic identities only. No impersonation or external account operations."""
import copy
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from check_pr_scope import ScopeError,evaluate,validate_policy,within,validate_file_modes,validate_binding
from publication_scan import scan_blob,scan_name,scan_content


class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.sha='a'*40
        self.policy=json.loads((Path(__file__).resolve().parents[2]/'.github/team-policy.json').read_text())
        self.policy['owner']={'login':'fixture-owner','id':900000001}
        for i,m in enumerate(self.policy['members']):
            if m['identity_status']=='VERIFIED':
                m.update(login='fixture-owner' if i==0 else f'fixture-member-{i}',id=900000001+i)
        self.member=self.policy['members'][2]
        self.user={k:self.member[k] for k in ('login','id')}
        self.member.update(code_paths=['app/cases/'],document_paths=[],scope_active=True)
        self.member['implementation_approval']={'approved_by':900000001,'plan_blob_sha':self.sha,'approved_paths':['app/cases/']}

    def files(self,path,status='modified',previous=None):
        f={'filename':path,'status':status}
        if previous: f['previous_filename']=previous
        return [f]

    def check(self,files=None,author=None,sha=None,count=None):
        files=files or self.files('app/cases/card.md')
        return evaluate(self.policy,author or self.user,files,len(files) if count is None else count,self.sha if sha is None else sha)

    def test_approved_scope_passes(self): self.assertIn('exact approved',self.check())
    def test_unknown_author_fails(self):
        with self.assertRaises(ScopeError): self.check(author={'id':1,'login':'unknown-fixture'})
    def test_login_without_numeric_identity_fails(self):
        with self.assertRaises(ScopeError): self.check(author={'id':3,'login':self.user['login']})
    def test_numeric_identity_with_wrong_login_fails(self):
        with self.assertRaises(ScopeError): self.check(author={'id':self.user['id'],'login':'renamed-fixture'})
    def test_pending_member_fails(self):
        m=self.member;m.update(id=None,login=None,identity_status='AWAITING_LOGIN',implementation_approval=None,scope_active=False,plan_scope_active=False)
        with self.assertRaises(ScopeError): self.check()
    def test_plan_only_before_approval_passes(self):
        self.member.update(implementation_approval=None,scope_active=False)
        self.assertIn('PLAN-only',self.check(self.files('plans/xiangze-zhu/PLAN.md')))
    def test_unapproved_implementation_fails(self):
        self.member.update(implementation_approval=None,scope_active=False)
        with self.assertRaises(ScopeError): self.check()
    def test_other_person_plan_fails(self):
        with self.assertRaises(ScopeError): self.check(self.files('plans/zaixuan-ji/PLAN.md'))
    def test_scope_escape_fails(self):
        with self.assertRaises(ScopeError): self.check(self.files('app/quant/card.md'))
    def test_directory_prefix_collision_fails(self):
        with self.assertRaises(ScopeError): self.check(self.files('app/cases-private/card.md'))
    def test_policy_self_change_fails(self):
        with self.assertRaises(ScopeError): self.check(self.files('.github/team-policy.json'))
    def test_workflow_change_fails(self):
        with self.assertRaises(ScopeError): self.check(self.files('.github/workflows/governance.yml'))
    def test_checker_change_fails(self):
        with self.assertRaises(ScopeError): self.check(self.files('scripts/check_pr_scope.py'))
    def test_rename_from_outside_fails(self):
        with self.assertRaises(ScopeError): self.check(self.files('app/cases/card.md','renamed','app/quant/card.md'))
    def test_rename_to_outside_fails(self):
        with self.assertRaises(ScopeError): self.check(self.files('app/quant/card.md','renamed','app/cases/card.md'))
    def test_rename_within_scope_passes(self): self.check(self.files('app/cases/b.md','renamed','app/cases/a.md'))
    def test_missing_rename_source_fails(self):
        with self.assertRaises(ScopeError): self.check(self.files('app/cases/b.md','renamed'))
    def test_plan_edit_mixed_with_implementation_fails(self):
        with self.assertRaises(ScopeError): self.check(self.files('plans/xiangze-zhu/PLAN.md')+self.files('app/cases/a.md'))
    def test_stale_plan_approval_fails(self):
        with self.assertRaises(ScopeError): self.check(sha='b'*40)
    def test_incomplete_file_list_fails(self):
        with self.assertRaises(ScopeError): self.check(count=2)
    def test_duplicate_file_list_fails(self):
        with self.assertRaises(ScopeError): self.check(self.files('app/cases/a.md')*2)
    def test_owner_passes_shared_file_without_self_review(self): self.check(self.files('.github/CODEOWNERS'),self.policy['owner'])
    def test_traversal_fails(self):
        for path in ['../secret','/etc/passwd','app/cases/../risk/a.md','app/cases\\..\\risk','materials//factors/a.md']:
            with self.subTest(path=path),self.assertRaises(ScopeError): self.check(self.files(path))
    def test_nonowner_approval_fails(self):
        self.member['implementation_approval']['approved_by']=self.user['id']
        with self.assertRaises(ScopeError): self.check()
    def test_approval_outside_role_module_fails(self):
        self.member['implementation_approval']['approved_paths']=['content/cases/']
        with self.assertRaises(ScopeError): self.check()
    def test_duplicate_identity_fails(self):
        m=copy.deepcopy(self.member);m.update(role='another-member',plan_path='plans/zaixuan-ji/PLAN.md');self.policy['members'].append(m)
        with self.assertRaises(ScopeError): validate_policy(self.policy)
    def test_pending_identity_cannot_include_approval(self):
        self.member['identity_status']='AWAITING_LOGIN'
        with self.assertRaises(ScopeError): validate_policy(self.policy)
    def test_credentials_detected_without_printing(self):
        self.assertTrue(scan_blob(('gh'+'p_'+'A'*40).encode()))
        self.assertTrue(scan_blob(('sk-'+'B'*32).encode()))
    def test_restricted_files_detected(self):
        for path in ['private/notes.md','research/paper.pdf','app.db','.env.local','data/trades.csv']:
            self.assertTrue(scan_name(path),path)
    def test_example_environment_name_allowed(self): self.assertFalse(scan_name('.env.example'))
    def test_reviewed_synthetic_file_allowed(self):
        p=Path(__file__).resolve().parents[2]/'examples/cn-synthetic.csv'
        self.assertFalse(scan_name('examples/cn-synthetic.csv'))
        self.assertFalse(scan_content('examples/cn-synthetic.csv',p.read_bytes()))
    def test_same_csv_path_with_unreviewed_bytes_fails(self):
        self.assertTrue(scan_content('examples/cn-synthetic.csv',b'date,symbol,close\nchanged,data,123\n'))

    def test_r3_missing_role_fails(self):
        self.policy['members'].pop()
        with self.assertRaises(ScopeError): validate_policy(self.policy)
    def test_r3_fifth_developer_fails(self):
        self.policy['members'][4]['is_developer']=True
        with self.assertRaises(ScopeError): validate_policy(self.policy)
    def test_old_spelling_cannot_be_eighth_role(self):
        m=copy.deepcopy(self.member);m['role']='xingze-zhu';self.policy['members'].append(m)
        with self.assertRaises(ScopeError): validate_policy(self.policy)
    def test_duplicate_alias_fails(self):
        self.policy['members'][1]['display_name_aliases']=['Xingze.Zhu']
        with self.assertRaises(ScopeError): validate_policy(self.policy)
    def test_non_developer_cannot_receive_code(self):
        self.policy['members'][4]['code_paths']=['research/submissions/yifan-mao/']
        with self.assertRaises(ScopeError): validate_policy(self.policy)
    def test_verified_non_developer_script_is_rejected(self):
        m=self.policy['members'][4];m.update(identity_status='VERIFIED',login='fixture-researcher',id=900000010)
        with self.assertRaises(ScopeError): self.check(self.files('research/submissions/yifan-mao/tool.py'),author={'login':m['login'],'id':m['id']})
    def test_inactive_plan_scope_fails(self):
        self.member['plan_scope_active']=False
        with self.assertRaises(ScopeError): self.check(self.files('plans/xiangze-zhu/PLAN.md'))
    def test_inactive_implementation_scope_fails(self):
        self.member['scope_active']=False
        with self.assertRaises(ScopeError): self.check()
    def test_member_cannot_own_shared_main(self):
        self.member['code_paths'].append('app/main.py')
        with self.assertRaises(ScopeError): validate_policy(self.policy)
    def test_owner_identity_must_match_roster(self):
        self.policy['owner']['id']=1
        with self.assertRaises(ScopeError): validate_policy(self.policy)

    def tree(self,path='app/cases/card.md',mode='100644',kind='blob'):
        return {'truncated':False,'tree':[{'path':path,'mode':mode,'type':kind}]}
    def test_regular_file_metadata_passes(self):
        validate_file_modes(self.files('app/cases/card.md'),self.tree(),self.tree())
    def test_symlink_and_submodule_fail(self):
        for mode,kind in [('120000','blob'),('160000','commit')]:
            with self.subTest(mode=mode),self.assertRaises(ScopeError):
                validate_file_modes(self.files('app/cases/card.md'),self.tree(),self.tree(mode=mode,kind=kind))
    def test_removing_symlink_is_not_normal_member_change(self):
        with self.assertRaises(ScopeError):
            validate_file_modes(self.files('app/cases/card.md','removed'),self.tree(mode='120000'),{'truncated':False,'tree':[]})
    def test_truncated_tree_fails(self):
        t=self.tree();t['truncated']=True
        with self.assertRaises(ScopeError): validate_file_modes(self.files('app/cases/card.md'),t,self.tree())
    def test_missing_tree_file_fails(self):
        with self.assertRaises(ScopeError): validate_file_modes(self.files('app/cases/card.md'),self.tree(),{'truncated':False,'tree':[]})
    def test_current_head_policy_binding_passes(self):
        p={'state':'open','head':{'sha':'b'*40},'base':{'sha':self.sha}}
        validate_binding(p,copy.deepcopy(p),self.sha)
    def test_new_head_cannot_use_old_check(self):
        p={'state':'open','head':{'sha':'b'*40},'base':{'sha':self.sha}};latest=copy.deepcopy(p);latest['head']['sha']='c'*40
        with self.assertRaises(ScopeError): validate_binding(p,latest,self.sha)
    def test_changed_policy_fails_closed(self):
        p={'state':'open','head':{'sha':'b'*40},'base':{'sha':self.sha}};latest=copy.deepcopy(p);latest['base']['sha']='c'*40
        with self.assertRaises(ScopeError): validate_binding(p,latest,self.sha)


if __name__=='__main__': unittest.main()
