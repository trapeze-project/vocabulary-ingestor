(in-package :mu-cl-resources)

(defparameter *max-group-sorted-properties* nil)

(define-resource class ()
  :class (s-prefix "rdfs:Class")
  :properties `(
                (:created :date ,(s-prefix "dct:created"))
                (:modified :date ,(s-prefix "dct:modified"))
                (:label :string ,(s-prefix "rdfs:label"))
                (:is-defined-by :uri ,(s-prefix "rdfs:isDefinedBy"))
                (:comment :string ,(s-prefix "rdfs:comment"))
                (:see-also :uri ,(s-prefix "rdfs:seeAlso"))
                (:term-status :string ,(s-prefix "vs:term_status"))
                (:creators :string-set ,(s-prefix "dct:creator"))
                (:description :string ,(s-prefix "dct:description"))
                )
  :has-one `((class :via ,(s-prefix "rdfs:subClassOf") :as "super-class"))
  :has-many `((class :via ,(s-prefix "rdfs:subClassOf") :inverse t :as "sub-classes"))
  :resource-base (s-prefix "rdfs:Class")
  :on-path "classes"
)

(define-resource property ()
  :class (s-prefix "rdf:Property")
  :properties `(
                (:created :date ,(s-prefix "dct:created"))
                (:modified :date ,(s-prefix "dct:modified"))
                (:label :string ,(s-prefix "rdfs:label"))
                (:is-defined-by :uri ,(s-prefix "rdfs:isDefinedBy"))
                (:comment :string ,(s-prefix "rdfs:comment"))
                (:term-status :string ,(s-prefix "vs:term_status"))
                (:creators :string-set ,(s-prefix "dct:creator"))
                (:description :string ,(s-prefix "dct:description"))
                )
  :has-one `((property :via ,(s-prefix "rdfs:subPropertyOf") :as "super-property"))
  :has-many `(
                (property :via ,(s-prefix "rdfs:subPropertyOf") :inverse t :as "sub-properties")
                (class :via ,(s-prefix "rdfs:range") :as "classes-in-range")
                (class :via ,(s-prefix "rdfs:domain") :as "classes-in-domain")
             )
  :resource-base (s-prefix "rdf:Property")
  :on-path "properties"
)