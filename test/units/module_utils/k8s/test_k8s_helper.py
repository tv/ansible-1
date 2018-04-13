# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

from ansible.compat.tests import unittest

__metaclass__ = type

import copy
import yaml

from ansible.module_utils.k8s.common import KubernetesAnsibleModuleHelper
from kubernetes.client import V1ObjectMeta, V1beta1IngressSpec, V1beta1Ingress, V1beta1IngressBackend, \
    V1beta1IngressRule, V1beta1HTTPIngressRuleValue, V1beta1HTTPIngressPath, V1Role, V1PolicyRule


class TestK8SHelper(unittest.TestCase):
    def test_list_in_list_without_keys_diff(self):
        ingress_yaml = """
        kind: Ingress
        apiVersion: v1beta1
        metadata:
          name: nginx
          namespace: default
        spec:
          rules:
          - host: vhost1
            http:
              paths:
              - backend:
                  serviceName: vhost1
                  servicePort: 80
        """

        new_ingress = yaml.load(ingress_yaml)

        api_version = new_ingress['apiVersion']
        kind = new_ingress['kind']

        k8s_meta = V1ObjectMeta()
        k8s_meta.name = "nginx"
        k8s_meta.namespace = "default"
        existing = V1beta1Ingress(
            "v1beta1",
            "Ingress",
            k8s_meta,
            V1beta1IngressSpec(
                None,
                [V1beta1IngressRule(
                    "vhost1",
                    V1beta1HTTPIngressRuleValue([
                        V1beta1HTTPIngressPath(
                            V1beta1IngressBackend("vhost1", 80)
                        )
                    ])
                )]
            )
        )

        k8s_obj = copy.deepcopy(existing)
        params = {
            "api_version": api_version,
            "kind": kind,
            "name": "nginx",
            "namespace": "default",
            "spec_rules": new_ingress['spec']['rules']
        }

        self.helper = KubernetesAnsibleModuleHelper(api_version=api_version, kind=kind, debug=True)
        self.helper.object_from_params(params, obj=k8s_obj)
        match, diff = self.helper.objects_match(self.helper.fix_serialization(existing), k8s_obj)

        assert match

    def test_list_diff_with_primitives(self):
        """This here to avoid regressions"""
        role_yaml = """
        kind: Role
        apiVersion: v1
        metadata:
          name: some-role
          namespace: default
        rules:
          - apiGroups: ["extensions", "apps"]
            resources: ["deployments"]
            verbs: ["get", "list"]
        """

        role = yaml.load(role_yaml)
        api_version = role['apiVersion']
        kind = role['kind']

        meta = V1ObjectMeta()
        meta.name = "some-role"
        meta.namespace = "default"
        rule = role['rules'][0]
        existing = V1Role(api_version, kind, meta, [
            V1PolicyRule(
                api_groups=rule['apiGroups'],
                resources=rule['resources'],
                verbs=rule['verbs']
            )
        ])

        k8s_obj = copy.deepcopy(existing)

        params = {
            "api_version": api_version,
            "kind": kind,
            "name": meta.name,
            "namespace": meta.namespace,
            "rules": role['rules']
        }

        self.helper = KubernetesAnsibleModuleHelper(api_version=api_version, kind=kind, debug=True)
        self.helper.object_from_params(params, obj=k8s_obj)
        match, diff = self.helper.objects_match(self.helper.fix_serialization(existing), k8s_obj)

        assert match
