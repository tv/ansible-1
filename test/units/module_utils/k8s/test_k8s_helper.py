# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

import copy

from ansible.compat.tests import unittest

__metaclass__ = type

import yaml

from ansible.module_utils.k8s.common import KubernetesAnsibleModuleHelper
from kubernetes.client import V1ObjectMeta, V1beta1IngressSpec, V1beta1Ingress, V1beta1IngressBackend, \
    V1beta1IngressRule, V1beta1HTTPIngressRuleValue, V1beta1HTTPIngressPath


class TestK8SHelper(unittest.TestCase):
    def test_foo_bar(self):
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
